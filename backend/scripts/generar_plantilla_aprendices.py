import pandas as pd
import os

def generar_plantilla():
    # Asegurar que exista la carpeta
    ruta_script = os.path.dirname(os.path.abspath(__file__))
    ruta_salida = os.path.join(ruta_script, "Plantilla_Cargue_Aprendices.xlsx")

    # Columnas requeridas
    data = {
        'Tipo de Documento': ['CC', 'TI'],
        'Número de Documento': ['1000222333', '1098765432'],
        'Nombres': ['Andres Felipe', 'Laura Valentina'],
        'Apellidos': ['Gomez', 'Sanchez'],
        'Ficha': ['2693821', '2693821'],
        'Correo Electrónico Institucional': ['andres.gomez@misena.edu.co', 'laura.sanchez@misena.edu.co'],
        'Teléfono': ['3158709236', '3201234567']
    }

    df = pd.DataFrame(data)

    try:
        with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Aprendices')
            
            # Ajustar ancho de columnas para mejor visualización
            worksheet = writer.sheets['Aprendices']
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter 
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column].width = adjusted_width

        print(f"Plantilla generada exitosamente en: {ruta_salida}")
    except Exception as e:
        print(f"Error generando plantilla: {e}")
        print("Asegúrate de tener instalados: pip install pandas openpyxl")

if __name__ == '__main__':
    generar_plantilla()
