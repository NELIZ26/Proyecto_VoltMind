# services/reportes.py
import os
import base64
import io
import smtplib
from email.message import EmailMessage
from fpdf import FPDF

def ensamblar_y_enviar_pdf(sesion_id: str, numero_ficha: str, nombre_programa: str, nombre_instructor: str, correo_destino: str, competencia: str, resultado_aprendizaje: str, lista_firmas: list):
    """
    Ensambla el PDF de asistencia en memoria RAM y lo envía por correo.
    Recibe los 8 parámetros desde el router para evitar errores de TypeError.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # --- ENCABEZADO DEL REPORTE ---
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "REPORTE OFICIAL DE ASISTENCIA - SENA", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, f"Programa: {nombre_programa}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Ficha: {numero_ficha}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Instructor: {nombre_instructor}", new_x="LMARGIN", new_y="NEXT")
    
    # 🟢 INYECCIÓN DE LOS NUEVOS CAMPOS EN EL PDF FÍSICO
    if competencia:
        pdf.cell(0, 8, f"Competencia: {competencia}", new_x="LMARGIN", new_y="NEXT")
    if resultado_aprendizaje:
        pdf.cell(0, 8, f"Resultado de Aprendizaje: {resultado_aprendizaje}", new_x="LMARGIN", new_y="NEXT")
        
    pdf.cell(0, 8, "-"*60, new_x="LMARGIN", new_y="NEXT")
    
    # --- LISTA DE APRENDICES Y FIRMAS ---
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(60, 10, "Documento", border=1)
    pdf.cell(80, 10, "Nombre", border=1)
    pdf.cell(50, 10, "Firma", border=1, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 10)
    
    for registro in lista_firmas:
        # 1. Limpiar el Base64
        b64_data = registro["firma_b64"].split(",")[1] if "," in registro["firma_b64"] else registro["firma_b64"]
        imagen_decodificada = base64.b64decode(b64_data)
        
        # 🚀 OPTIMIZACIÓN 1: En lugar de crear un archivo '.png' en el disco, 
        # convertimos los bytes en un flujo de memoria RAM.
        img_stream = io.BytesIO(imagen_decodificada)
        
        # 3. Insertar fila en la tabla del PDF
        y_actual = pdf.get_y()
        pdf.cell(60, 20, registro["documento"], border=1)
        pdf.cell(80, 20, registro["nombre"], border=1)
        pdf.cell(50, 20, "", border=1)
        
        # 4. Pegar la imagen directamente desde la RAM
        pdf.image(img_stream, x=155, y=y_actual + 2, w=40, h=16)
        pdf.ln(20)

    # 🚀 OPTIMIZACIÓN 2: Generar el PDF como una cadena de Bytes en RAM 
    # en lugar de usar pdf.output("ruta.pdf")
    pdf_bytes = pdf.output()
    
    print(f"✅ ¡ÉXITO! PDF ensamblado en Memoria RAM para la sesión {sesion_id}")
    
    # --- ENVÍO DE CORREO ---
    # --- ENVÍO DE CORREO ---
    email_origen = os.getenv("SMTP_EMAIL")
    password_origen = os.getenv("SMTP_PASSWORD")

    # 🔍 PRINT DE CONTROL: Verifiquemos qué string está viajando desde el frontend
    print(f"✉️ Intentando enviar correo desde [{email_origen}] hacia [{correo_destino}]...")

    msg = EmailMessage()
    msg["Subject"] = f"Reporte de Asistencia - Ficha {numero_ficha}"
    msg["From"] = email_origen 
    msg["To"] = correo_destino
    
    cuerpo_mensaje = f"""Cordial saludo, instructor {nombre_instructor}.

El sistema VoltMind ha finalizado con éxito la sesión de aprendizaje.
Adjunto a este correo encontrará la planilla oficial de asistencia.

Detalles de la sesión:
- Competencia: {competencia if competencia else 'No registrada'}
- RAP: {resultado_aprendizaje if resultado_aprendizaje else 'No registrado'}

Este es un mensaje automático, por favor no responda."""
    
    msg.set_content(cuerpo_mensaje, charset='utf-8')
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=f"Asistencia_{numero_ficha}_{sesion_id[-6:]}.pdf")
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email_origen, password_origen)
            smtp.send_message(msg)
        print(f"✅ ¡ÉXITO! Correo enviado satisfactoriamente a: {correo_destino}")
    except Exception as e:
        # 🚀 REPR y TYPE nos dirán el nombre técnico exacto del error de Google (ej: SMTPAuthenticationError)
        print(f"❌ Error de tipo [{type(e).__name__}]: {repr(e)}")