import random
import base64
import tempfile
import os
import smtplib
from services.dataverse import consultar_dataverse
from dotenv import load_dotenv

from email.message import EmailMessage
from fpdf import FPDF
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta

load_dotenv()

memoria_pines = {}


class PinCreate(BaseModel):
    documento_aprendiz: str

class PinValidate(BaseModel):
    pin: str
    sesion_id: str

router = APIRouter(prefix="/api/asistencia", 
tags=["Asistencia"])

# ==========================================
# 🧠 MEMORIA EFÍMERA PARA FIRMAS
# Estructura: {"sesion_id": [{"nombre": "Juan", "doc": "123", "firma_b64": "..."}]}
# ==========================================
firmas_temporales = {}

class FirmaCreate(BaseModel):
    sesion_id: str
    documento_aprendiz: str
    nombre_aprendiz: str
    firma_base64: str # El string largo que manda Vue

class CierreSesion(BaseModel):
    sesion_id: str
    numero_ficha: str
    nombre_programa: str
    nombre_instructor: str
    correo_destino: str

@router.post("/guardar-firma")
async def guardar_firma_temporal(datos: FirmaCreate):
    # Si la sesión no existe en memoria, la creamos
    if datos.sesion_id not in firmas_temporales:
        firmas_temporales[datos.sesion_id] = []
        
    # Guardamos la firma en la RAM
    firmas_temporales[datos.sesion_id].append({
        "nombre": datos.nombre_aprendiz,
        "documento": datos.documento_aprendiz,
        "firma_b64": datos.firma_base64
    })
    
    return {"mensaje": "Firma almacenada en caché temporalmente."}

# ==========================================
# 📄 LÓGICA DE GENERACIÓN DE PDF Y ENVÍO (Se ejecuta en segundo plano)
# ==========================================
def ensamblar_y_enviar_pdf(datos_cierre: CierreSesion, lista_firmas: list):
    pdf = FPDF()
    pdf.add_page()
    
    # --- ENCABEZADO DEL REPORTE ---
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "REPORTE OFICIAL DE ASISTENCIA - SENA", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, f"Programa: {datos_cierre.nombre_programa}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Ficha: {datos_cierre.numero_ficha}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Instructor: {datos_cierre.nombre_instructor}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "-"*60, new_x="LMARGIN", new_y="NEXT")
    
    # --- LISTA DE APRENDICES Y FIRMAS ---
    archivos_temporales = [] # Para borrar las imágenes después de usarlas
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(60, 10, "Documento", border=1)
    pdf.cell(80, 10, "Nombre", border=1)
    pdf.cell(50, 10, "Firma", border=1, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 10)
    
    for registro in lista_firmas:
        # 1. Limpiar el Base64 (quitar el 'data:image/png;base64,')
        b64_data = registro["firma_b64"].split(",")[1] if "," in registro["firma_b64"] else registro["firma_b64"]
        imagen_decodificada = base64.b64decode(b64_data)
        
        # 2. Crear un archivo de imagen temporal en el disco del servidor
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp_img.write(imagen_decodificada)
        temp_img.close()
        archivos_temporales.append(temp_img.name)
        
        # 3. Insertar fila en la tabla del PDF
        y_actual = pdf.get_y()
        pdf.cell(60, 20, registro["documento"], border=1)
        pdf.cell(80, 20, registro["nombre"], border=1)
        pdf.cell(50, 20, "", border=1) # Celda vacía para el cuadro
        
        # 4. Pegar la imagen de la firma dentro del cuadro
        pdf.image(temp_img.name, x=155, y=y_actual + 2, w=40, h=16)
        pdf.ln(20)

    # Guardar PDF temporalmente
    ruta_pdf = os.path.join(os.getcwd(), f"Asistencia_{datos_cierre.numero_ficha}.pdf")
    pdf.output(ruta_pdf)
    
    print(f"✅ ¡ÉXITO! EL PDF SE GUARDÓ AQUÍ: {ruta_pdf}")
    
    # 🟢 1. Leemos las credenciales PRIMERO
    email_origen = os.getenv("SMTP_EMAIL")
    password_origen = os.getenv("SMTP_PASSWORD")

    # --- ENVÍO DE CORREO ---
    msg = EmailMessage()
    msg["Subject"] = f"Reporte de Asistencia - Ficha {datos_cierre.numero_ficha}"
    msg["From"] = email_origen # 🟢 2. Usamos la misma variable para que Microsoft no bloquee el envío
    msg["To"] = datos_cierre.correo_destino
    
    # 🟢 3. Pegado a la izquierda para que el correo se lea bien formateado
    cuerpo_mensaje = f"""Cordial saludo, instructor {datos_cierre.nombre_instructor}.

El sistema VoltMind ha finalizado con éxito la sesión de aprendizaje.
Adjunto a este correo encontrará la planilla oficial de asistencia correspondiente a la ficha {datos_cierre.numero_ficha}.

Este es un mensaje automático, por favor no responda a esta dirección."""
    
    # Forzamos la codificación a UTF-8 para soportar tildes y la letra Ñ
    msg.set_content(cuerpo_mensaje, charset='utf-8')
    
    with open(ruta_pdf, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=f"Asistencia_{datos_cierre.numero_ficha}.pdf")
    
    try:
        import smtplib
        # Conexión directa y segura para Gmail
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email_origen, password_origen)
            smtp.send_message(msg)
        print(f"✅ ¡ÉXITO! Correo enviado a: {datos_cierre.correo_destino}")
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")

    # --- AUTODESTRUCCIÓN (Limpieza total) ---
    # os.remove(ruta_pdf)
    #for temp_img_path in archivos_temporales:
    #    os.remove(temp_img_path)

@router.post("/generar-reporte")
async def generar_reporte_asistencia(datos: CierreSesion, background_tasks: BackgroundTasks):
    lista_firmas = firmas_temporales.get(datos.sesion_id, [])
    
    if not lista_firmas:
        raise HTTPException(status_code=400, detail="No hay firmas registradas para esta sesión.")
    
    # Lanzar el ensamble y envío al fondo para no hacer esperar al frontend
    background_tasks.add_task(ensamblar_y_enviar_pdf, datos, lista_firmas)
    
    # 💥 Destruir las firmas de la memoria RAM inmediatamente
    del firmas_temporales[datos.sesion_id]
    
    return {"mensaje": "Reporte en proceso. Se enviará al correo del instructor en breve."}


@router.post("/generar-pin")
async def generar_pin(datos: PinCreate):
    ahora = datetime.now()
    
    # Limpiar pines viejos
    pines_a_borrar = [p for p, v in memoria_pines.items() if v["expira"] < ahora]
    for p in pines_a_borrar:
        del memoria_pines[p]

    # Generar nuevo PIN
    while True:
        nuevo_pin = str(random.randint(1000, 9999))
        if nuevo_pin not in memoria_pines:
            break

    memoria_pines[nuevo_pin] = {
        "documento": datos.documento_aprendiz,
        "expira": ahora + timedelta(seconds=65)
    }
    
    return {"pin": nuevo_pin}


@router.post("/validar-pin")
async def validar_pin(datos: PinValidate):
    ahora = datetime.now()
    info_pin = memoria_pines.get(datos.pin)

    if not info_pin:
        raise HTTPException(status_code=400, detail="PIN incorrecto o no existe.")
    
    if ahora > info_pin["expira"]:
        del memoria_pines[datos.pin] 
        raise HTTPException(status_code=400, detail="El PIN ha expirado.")

    doc_aprendiz = info_pin["documento"]
    del memoria_pines[datos.pin]

    return {
        "mensaje": "Asistencia validada con éxito", 
        "documento_aprendiz": doc_aprendiz
    }
