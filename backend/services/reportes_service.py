# services/reportes_service.py
import os
import base64
import io
import smtplib
import urllib.parse
from core.logger import log
from datetime import datetime, timedelta
from email.message import EmailMessage
from fpdf import FPDF
from services.dataverse import obtener_cliente

def obtener_rango_semana_actual():
    hoy = datetime.now()
    inicio = hoy - timedelta(days=hoy.weekday())
    fin = inicio + timedelta(days=4)
    return (
        inicio.replace(hour=0, minute=0, second=0).isoformat() + "Z",
        fin.replace(hour=23, minute=59, second=59).isoformat() + "Z"
    )

class FFPDF_Horizontal(FPDF):
    pass

async def compilar_y_enviar_matriz_semanal(
    numero_ficha: str, 
    nombre_programa: str, 
    nombre_instructor: str, 
    correo_destino: str, 
    nombre_ambiente: str = "Por definir", 
    horario: str = "Por definir", 
    firmas_en_vivo: list = None
):
    """
    Busca los datos de la semana en Dataverse, auto-detecta la información real del 
    encabezado desde la DB, traduce la jornada a rangos de hora, fusiona las firmas y despacha el PDF.
    """
    fecha_inicio, fecha_fin = obtener_rango_semana_actual()
    client = obtener_cliente()

    try:
        # Lógica de fechas (De Lunes a Domingo - 7 días)
        hoy = datetime.now()
        lunes = hoy - timedelta(days=hoy.weekday())
        nombres_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dias_estructura = [( (lunes + timedelta(days=i)).strftime("%d/%m/%Y"), nombres_dias[i] ) for i in range(7)]
        
        # Calcular el mes actual en Español
        meses_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        mes_actual = meses_es[hoy.month - 1]
        
        # 1. 🟢 CONSULTA MAESTRA DE FICHA: Extraemos Programa y Jornada reales
        url_ficha = f"cr6a3_fichas?$filter=cr6a3_numero_ficha eq '{numero_ficha}'&$select=cr6a3_fichaid,cr6a3_nombre_programa,cr6a3_jornada"
        resp_ficha = await client.get(url_ficha)
        fichas_data = resp_ficha.json().get("value", [])
        if not fichas_data:
            log.warning(f"La ficha {numero_ficha} no existe en Dataverse.")
            return {"error": f"Ficha {numero_ficha} inexistente."}
        
        ficha_obj = fichas_data[0]
        ficha_id = ficha_obj["cr6a3_fichaid"]
        
        # Asignamos valores reales de la DB con fallbacks seguros de la interfaz
        programa_db = ficha_obj.get("cr6a3_nombre_programa", nombre_programa)
        
        # 🟢 NUEVO: TRADUCTOR DE JORNADA A RANGO HORARIO
        jornada_raw = ficha_obj.get("cr6a3_jornada@OData.Community.Display.V1.FormattedValue", horario)
        jornada_lower = str(jornada_raw).strip().lower() # Normalizamos a minúsculas para buscar fácilmente
        
        if "mañana" in jornada_lower:
            horario_db = "07:00 - 12:00"
        elif "tarde" in jornada_lower:
            horario_db = "14:00 - 18:00"
        elif "noch" in jornada_lower or "nocturn" in jornada_lower:
            horario_db = "18:00 - 23:00"
        else:
            horario_db = jornada_raw # Fallback si en Dataverse escribieron algo distinto a estas tres
            
        # 2. Obtener lista completa de Aprendices matriculados
        url_aps = f"cr6a3_aprendizs?$filter=_cr6a3_fichavinculad_value eq '{ficha_id}'&$select=cr6a3_aprendizid,cr6a3_documento_de_identidad,cr6a3_nombre_completo"
        resp_aps = await client.get(url_aps)
        aprendices_data = resp_aps.json().get("value", [])

        matriz_asistencia = {}
        mapa_ap = {}
        for ap in aprendices_data:
            doc = ap["cr6a3_documento_de_identidad"]
            mapa_ap[ap["cr6a3_aprendizid"]] = doc
            matriz_asistencia[doc] = {"nombre": ap["cr6a3_nombre_completo"], "asistencias": {}}

        # 3. 🟢 CONSULTA DE SESIONES: Buscamos historial e identificamos el Ambiente de Formación
        filtro_sesiones = f"_cr6a3_ficha_value eq '{ficha_id}' and cr6a3_hora_entrada ge {fecha_inicio} and cr6a3_hora_entrada le {fecha_fin}"
        url_ss = f"cr6a3_sesiones_de_clases?$filter={urllib.parse.quote(filtro_sesiones)}&$select=cr6a3_sesiones_de_claseid,cr6a3_hora_entrada,_cr6a3_ambiente_formacion_value"
        resp_ss = await client.get(url_ss)
        sesiones_data = resp_ss.json().get("value", [])

        ambiente_db = nombre_ambiente
        
        # 4. Cruzar Registro de Asistencias y Firmas históricas
        if sesiones_data:
            ambiente_db = sesiones_data[0].get("_cr6a3_ambiente_formacion_value@OData.Community.Display.V1.FormattedValue", nombre_ambiente)
            
            mapa_ss = {s["cr6a3_sesiones_de_claseid"]: s["cr6a3_hora_entrada"].split("T")[0] for s in sesiones_data}
            filtro_asis = " or ".join([f"_cr6a3_sesiones_de_clase_value eq '{sid}'" for sid in mapa_ss.keys()])
            url_as = f"cr6a3_registro_de_asistencias?$filter={urllib.parse.quote(filtro_asis)}&$select=_cr6a3_aprendiz_value,_cr6a3_sesiones_de_clase_value,cr6a3_firma_digital"
            
            resp_as = await client.get(url_as)
            asistencias_data = resp_as.json().get("value", [])

            for asis in asistencias_data:
                doc_ap = mapa_ap.get(asis.get("_cr6a3_aprendiz_value"))
                fecha_clase = mapa_ss.get(asis.get("_cr6a3_sesiones_de_clase_value"))
                
                if fecha_clase:
                    fecha_obj = datetime.strptime(fecha_clase, "%Y-%m-%d")
                    fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
                    if doc_ap:
                        matriz_asistencia[doc_ap]["asistencias"][fecha_formateada] = asis.get("cr6a3_firma_digital")
        
        # Inyección en caliente desde Redis
        if firmas_en_vivo:
            hoy_str = hoy.strftime("%d/%m/%Y")
            for firma_v in firmas_en_vivo:
                doc_ap = firma_v.get("documento")
                b64 = firma_v.get("firma_b64")
                if doc_ap in matriz_asistencia:
                    matriz_asistencia[doc_ap]["asistencias"][hoy_str] = b64

        # 5. Dibujar el PDF Horizontal con el Horario Traducido
        pdf_bytes = ensamblar_pdf_matriz_semanal(
            matriz_datos=matriz_asistencia,
            numero_ficha=numero_ficha,
            programa=programa_db,       
            instructor=nombre_instructor,
            dias_estructura=dias_estructura,
            ambiente=ambiente_db,       
            mes=mes_actual,             
            horario=horario_db          # 🟢 Pasamos la hora ya formateada al PDF
        )
        
        # 6. Guardado Físico
        nombre_archivo = f"Matriz_Semanal_Ficha_{numero_ficha}.pdf"
        ruta_guardado = os.path.join("storage", nombre_archivo)
        os.makedirs("storage", exist_ok=True)
        with open(ruta_guardado, "wb") as f:
            f.write(pdf_bytes)
            
        # 7. Despacho SMTP
        email_origen = os.getenv("SMTP_EMAIL")
        password_origen = os.getenv("SMTP_PASSWORD")

        msg = EmailMessage()
        msg["Subject"] = f"Matriz Semanal de Asistencia - Ficha {numero_ficha}"
        msg["From"] = email_origen 
        msg["To"] = correo_destino
        
        cuerpo = f"Cordial saludo instructor {nombre_instructor}.\n\nSe adjunta la matriz de asistencia semanal oficial generada automáticamente por VoltMind para la ficha {numero_ficha}."
        msg.set_content(cuerpo, charset='utf-8')
        msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=f"Sabana_Asistencia_{numero_ficha}.pdf")
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email_origen, password_origen)
            smtp.send_message(msg)
            
        log.info(f"Matriz semanal procesada directamente desde Dataverse y enviada con éxito a {correo_destino}")
        return {"mensaje": "Reporte enviado con éxito."}

    except Exception as e:
        log.error(f"Error generando/enviando matriz semanal: {repr(e)}", exc_info=True)
        raise e
    
def ensamblar_pdf_matriz_semanal(matriz_datos: dict, numero_ficha: str, programa: str, instructor: str, dias_estructura: list, ambiente: str = "", mes: str = "", horario: str = ""):
    """
    Dibuja el PDF respetando la simetría milimétrica del formato SENA.
    Se ocultan los textos de Sábado y Domingo, se centran las leyendas de asistencia,
    y se inyectan dinámicamente los datos del Aula, Mes y Horario.
    """
    pdf = FFPDF_Horizontal(orientation="L", unit="mm", format="A4")
    pdf.set_margins(10, 10, 10)
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    
    W_TOTAL = 277 
    
    # 🟢 1. FRASE CRÍTICA SUPERIOR IZQUIERDA
    pdf.set_font("helvetica", "I", 7)
    pdf.cell(W_TOTAL, 4, "Documento de Trabajo No Controlado -16-10-2019", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    
    # --- 📐 MATEMÁTICA DE LA CUADRÍCULA ESTRICTA ---
    w_no = 8       
    w_nom = 73     
    w_dia = 28     
    w_titulos = 35 
    
    w_hasta_jueves = w_no + w_nom + (w_dia * 4)  
    w_hasta_viernes = w_no + w_nom + (w_dia * 5) 
    
    w_bloque_ficha = W_TOTAL - w_hasta_jueves 
    w_ambiente = w_dia * 2      
    w_mes = W_TOTAL - w_hasta_jueves - w_ambiente               
    w_sab_dom = W_TOTAL - w_hasta_viernes       
    
    # 🟢 2. ENCABEZADO PRINCIPAL
    pdf.set_font("helvetica", "B", 10)
    pdf.multi_cell(W_TOTAL, 5, "CONTROL DE ASISTENCIAS DE APRENDICES AL PROCESO FORMATIVO\nSENA - REGIONAL PUTUMAYO", border=1, align="C")
    
    pdf.set_x(10) 
    
    programa_limpio = str(programa).replace('\n', ' ').strip()
    ficha_limpia = str(numero_ficha).replace('\n', '').strip()

    # Fila 1: Programa de Formación y Ficha
    pdf.set_font("helvetica", "B", 8)
    pdf.cell(w_titulos, 8, "Programa de formación:", border=1)
    pdf.set_font("helvetica", "", 8)
    pdf.cell(w_hasta_jueves - w_titulos, 8, programa_limpio[:80], border=1, align="C") 
    pdf.set_font("helvetica", "B", 8)
    # Mantengo tu ajuste de "ficha de caracterizacion"
    pdf.cell(w_bloque_ficha, 8, f"N° de ficha de caracterizacion: {ficha_limpia}", border=1, align="C", new_x="LMARGIN", new_y="NEXT")
    
    # Fila 2: Competencia, Ambiente y Mes
    y_start = pdf.get_y()
    x_start = pdf.get_x()

    pdf.set_font("helvetica", "B", 8)
    pdf.cell(w_titulos, 16, "Competencia:", border=1)
    pdf.set_font("helvetica", "", 8)
    pdf.cell(w_hasta_jueves - w_titulos, 16, "", border=1, align="C") 

    x_derecha = pdf.get_x() 

    pdf.set_font("helvetica", "B", 8)
    pdf.cell(w_ambiente, 8, "Ambiente de Aprendizaje", border=1, align="C")
    pdf.cell(w_mes, 8, "Mes", border=1, align="C")

    pdf.set_xy(x_derecha, y_start + 8)
    pdf.set_font("helvetica", "", 8)
    
    # 🔥 CORRECCIÓN: Inyección real de variables de Ambiente y Mes
    pdf.cell(w_ambiente, 8, ambiente.upper()[:30], border=1, align="C") 
    pdf.cell(w_mes, 8, mes.upper(), border=1, align="C")     

    pdf.set_xy(x_start, y_start + 16) 
    
    # Fila 3: Resultado de Aprendizaje y Horario
    y_start = pdf.get_y()
    pdf.set_font("helvetica", "B", 8)
    pdf.multi_cell(w_titulos, 6, "Resultado de\naprendizaje:", border=1, align="L") 
    
    pdf.set_xy(x_start + w_titulos, y_start)
    
    pdf.set_font("helvetica", "", 8)
    pdf.cell(w_hasta_viernes - w_titulos, 12, "", border=1, align="C") 
    
    pdf.set_font("helvetica", "B", 8)
    pdf.cell(w_dia, 12, "Horario:", border=1, align="C") 
    pdf.set_font("helvetica", "", 8)
    
    # 🔥 CORRECCIÓN: Inyección real de la variable Horario
    pdf.cell(w_sab_dom - w_dia, 12, horario, border=1, align="C", new_x="LMARGIN", new_y="NEXT") 
    
    # Fila 4: Instructor y Leyendas
    y_start = pdf.get_y()
    pdf.set_font("helvetica", "B", 8)
    pdf.cell(w_titulos, 12, "Instructor:", border=1)
    pdf.set_font("helvetica", "", 8)
    pdf.cell(w_hasta_viernes - w_titulos, 12, instructor.upper(), border=1, align="C")
    
    x_derecha = pdf.get_x() 
    pdf.set_font("helvetica", "I", 8)
    pdf.cell(w_sab_dom, 6, "Asistió: Firma", border=1, align="C") 
    
    pdf.set_xy(x_derecha, y_start + 6)
    pdf.cell(w_sab_dom, 6, "No asistió: X", border=1, align="C")
    
    pdf.set_xy(x_start, y_start + 12) 
    
    # --- CABECERA DE DÍAS CON LÍNEA DIAGONAL INTEGRADA ---
    pdf.set_font("helvetica", "B", 8)
    
    pdf.cell(w_no, 6, "No.", border="LTR", align="C")
    
    x_diagonal = pdf.get_x()
    y_diagonal = pdf.get_y()
    pdf.cell(w_nom, 6, "                                           Fecha", border="LTR", align="L")
    
    for fecha, dia in dias_estructura:
        texto_fecha = "" if dia in ["Sábado", "Domingo"] else fecha
        pdf.cell(w_dia, 6, texto_fecha, border=1, align="C")
    pdf.cell(0, 6, "", new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(w_no, 6, "", border="LBR", align="C")
    
    pdf.set_xy(x_diagonal, y_diagonal + 6)
    pdf.cell(w_nom, 6, " Nombres y apellidos", border="LBR", align="L")
    
    for fecha, dia in dias_estructura:
        texto_dia = "" if dia in ["Sábado", "Domingo"] else dia
        pdf.cell(w_dia, 6, texto_dia, border=1, align="C")
    pdf.cell(0, 6, "", new_x="LMARGIN", new_y="NEXT")
    
    pdf.line(x_diagonal, y_diagonal, x_diagonal + w_nom, y_diagonal + 12)
    
    # --- FILAS DE APRENDICES (CUADRÍCULA COMPACTADA) ---
    pdf.set_font("helvetica", "", 7)
    contador = 1
    CARPETA_FIRMAS = os.path.join("storage", "firmas")
    row_h = 8 
    
    for doc, info in matriz_datos.items():
        y_actual = pdf.get_y()
        if y_actual > 185: 
            pdf.add_page()
            y_actual = pdf.get_y()
            
        pdf.cell(w_no, row_h, str(contador), border=1, align="C")
        pdf.cell(w_nom, row_h, info["nombre"][:45], border=1)
        
        x_actual = pdf.get_x()
        for fecha, dia in dias_estructura:
            firma = info["asistencias"].get(fecha)
            pdf.cell(w_dia, row_h, "", border=1)
            
            if firma:
                archivo_limpio = str(firma).strip()
                if archivo_limpio.upper() == "X":
                    pdf.text(x_actual + (w_dia/2) - 1, y_actual + 5.5, "X")
                else:
                    ruta_img = os.path.join(CARPETA_FIRMAS, archivo_limpio)
                    if not os.path.exists(ruta_img): ruta_img += ".png"
                    if os.path.exists(ruta_img):
                        pdf.image(ruta_img, x=x_actual + 1, y=y_actual + 1, w=w_dia - 2, h=6)
            x_actual += w_dia
            
        pdf.cell(0, row_h, "", new_x="LMARGIN", new_y="NEXT")
        contador += 1
        
    pdf.ln(10)
    pdf.cell(60, 0, "", border="T", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "B", 8)
    pdf.cell(60, 5, "Firma Instructor:")
    
    return pdf.output()