"""
Módulo de exportación de datos para el Homologador de Aplicaciones.
Funciones para exportar datos a CSV, Excel y otros formatos.
"""

import os
import logging
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from core.storage import get_homologation_repository, get_audit_repository
from core.audit import get_audit_logger

logger = logging.getLogger(__name__)


class ExportError(Exception):
    """Excepción personalizada para errores de exportación."""
    pass


class DataExporter:
    """Clase para manejar exportaciones de datos."""
    
    def __init__(self):
        self.homolog_repo = get_homologation_repository()
        self.audit_repo = get_audit_repository()
        self.audit_logger = get_audit_logger()
    
    def export_homologations_to_csv(self, filename: str, filters: Optional[Dict[str, Any]] = None, 
                                   user_id: Optional[int] = None) -> bool:
        """Exporta homologaciones a CSV usando el módulo csv estándar."""
        try:
            # Obtener datos
            if filters and filters.get('search_term'):
                data = self.homolog_repo.search(filters['search_term'])
            else:
                filter_dict = self._prepare_filters(filters)
                data = self.homolog_repo.get_all(filter_dict)
            
            # Convertir a lista de diccionarios
            records = [dict(row) for row in data]
            
            if not records:
                raise ExportError("No hay datos para exportar")
            
            # Escribir CSV
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                # Headers personalizados
                fieldnames = [
                    'id', 'real_name', 'logical_name', 'kb_url',
                    'homologation_date', 'has_previous_versions', 'repository_location',
                    'details', 'created_by_username', 'created_by_full_name',
                    'created_at', 'updated_at'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                
                # Headers en español
                spanish_headers = {
                    'id': 'ID',
                    'real_name': 'Nombre Real',
                    'logical_name': 'Nombre Lógico',
                    'kb_url': 'URL Documentación',
                    'homologation_date': 'Fecha Homologación',
                    'has_previous_versions': 'Versiones Previas',
                    'repository_location': 'Repositorio',
                    'details': 'Detalles',
                    'created_by_username': 'Usuario Creador',
                    'created_by_full_name': 'Nombre Completo Creador',
                    'created_at': 'Fecha Creación',
                    'updated_at': 'Última Actualización'
                }
                
                writer.writerow(spanish_headers)
                
                # Procesar datos
                for record in records:
                    # Formatear campos específicos
                    processed_record = self._process_record_for_export(record)
                    writer.writerow(processed_record)
            
            # Log de exportación
            if user_id:
                self.audit_logger.log_data_export(
                    user_id=user_id,
                    export_type="CSV_HOMOLOGATIONS",
                    record_count=len(records),
                    filters=filters
                )
            
            logger.info(f"Exportación CSV exitosa: {filename} ({len(records)} registros)")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando a CSV: {e}")
            raise ExportError(f"Error exportando a CSV: {e}")
    
    def export_homologations_to_excel(self, filename: str, filters: Optional[Dict[str, Any]] = None,
                                     user_id: Optional[int] = None) -> bool:
        """Exporta homologaciones a Excel usando pandas."""
        if not PANDAS_AVAILABLE:
            raise ExportError("pandas no está disponible. Use exportación CSV.")
        
        try:
            # Obtener datos
            if filters and filters.get('search_term'):
                data = self.homolog_repo.search(filters['search_term'])
            else:
                filter_dict = self._prepare_filters(filters)
                data = self.homolog_repo.get_all(filter_dict)
            
            # Convertir a DataFrame
            records = [dict(row) for row in data]
            
            if not records:
                raise ExportError("No hay datos para exportar")
            
            df = pd.DataFrame(records)
            
            # Reordenar y renombrar columnas
            column_mapping = {
                'id': 'ID',
                'real_name': 'Nombre Real',
                'logical_name': 'Nombre Lógico',
                'kb_url': 'URL Documentación',
                'homologation_date': 'Fecha Homologación',
                'has_previous_versions': 'Versiones Previas',
                'repository_location': 'Repositorio',
                'details': 'Detalles',
                'created_by_username': 'Usuario Creador',
                'created_by_full_name': 'Nombre Completo Creador',
                'created_at': 'Fecha Creación',
                'updated_at': 'Última Actualización'
            }
            
            # Seleccionar y renombrar columnas existentes
            existing_columns = [col for col in column_mapping.keys() if col in df.columns]
            df_export = df[existing_columns].copy()
            df_export.rename(columns=column_mapping, inplace=True)
            
            # Formatear datos
            df_export = self._format_dataframe_for_export(df_export)
            
            # Exportar con formato
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df_export.to_excel(writer, sheet_name='Homologaciones', index=False)
                
                # Formatear hoja
                workbook = writer.book
                worksheet = writer.sheets['Homologaciones']
                
                # Ajustar ancho de columnas
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Formatear header
                from openpyxl.styles import Font
                header_font = Font(bold=True)
                for cell in worksheet[1]:
                    cell.font = header_font
            
            # Log de exportación
            if user_id:
                self.audit_logger.log_data_export(
                    user_id=user_id,
                    export_type="EXCEL_HOMOLOGATIONS",
                    record_count=len(records),
                    filters=filters
                )
            
            logger.info(f"Exportación Excel exitosa: {filename} ({len(records)} registros)")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando a Excel: {e}")
            raise ExportError(f"Error exportando a Excel: {e}")
    
    def export_audit_trail_to_csv(self, filename: str, filters: Optional[Dict[str, Any]] = None,
                                 user_id: Optional[int] = None) -> bool:
        """Exporta trail de auditoría a CSV."""
        try:
            # Obtener datos de auditoría
            audit_data = self.audit_repo.get_audit_trail(filters)
            records = [dict(row) for row in audit_data]
            
            if not records:
                raise ExportError("No hay datos de auditoría para exportar")
            
            # Escribir CSV
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    'id', 'action', 'table_name', 'record_id',
                    'username', 'full_name', 'timestamp',
                    'old_values', 'new_values', 'ip_address'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                
                # Headers en español
                spanish_headers = {
                    'id': 'ID',
                    'action': 'Acción',
                    'table_name': 'Tabla',
                    'record_id': 'ID Registro',
                    'username': 'Usuario',
                    'full_name': 'Nombre Completo',
                    'timestamp': 'Fecha y Hora',
                    'old_values': 'Valores Anteriores',
                    'new_values': 'Valores Nuevos',
                    'ip_address': 'Dirección IP'
                }
                
                writer.writerow(spanish_headers)
                
                # Procesar datos
                for record in records:
                    processed_record = self._process_audit_record_for_export(record)
                    writer.writerow(processed_record)
            
            # Log de exportación
            if user_id:
                self.audit_logger.log_data_export(
                    user_id=user_id,
                    export_type="CSV_AUDIT_TRAIL",
                    record_count=len(records),
                    filters=filters
                )
            
            logger.info(f"Exportación auditoría CSV exitosa: {filename} ({len(records)} registros)")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando auditoría a CSV: {e}")
            raise ExportError(f"Error exportando auditoría a CSV: {e}")
    
    def _prepare_filters(self, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepara filtros para consulta."""
        if not filters:
            return {}
        
        filter_dict = {}
        
        if filters.get('real_name'):
            filter_dict['real_name'] = filters['real_name']
        
        if filters.get('logical_name'):
            filter_dict['logical_name'] = filters['logical_name']
        
        if filters.get('date_from'):
            filter_dict['date_from'] = filters['date_from']
        
        if filters.get('date_to'):
            filter_dict['date_to'] = filters['date_to']
        
        if filters.get('repository_location'):
            filter_dict['repository_location'] = filters['repository_location']
        
        return filter_dict
    
    def _process_record_for_export(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un registro para exportación."""
        processed = record.copy()
        
        # Formatear booleanos
        if 'has_previous_versions' in processed:
            processed['has_previous_versions'] = 'Sí' if processed['has_previous_versions'] else 'No'
        
        # Formatear fechas
        for date_field in ['homologation_date', 'created_at', 'updated_at']:
            if date_field in processed and processed[date_field]:
                try:
                    if 'T' in str(processed[date_field]):
                        dt = datetime.fromisoformat(str(processed[date_field]).replace('Z', '+00:00'))
                        processed[date_field] = dt.strftime('%d/%m/%Y %H:%M:%S')
                    else:
                        processed[date_field] = str(processed[date_field])
                except:
                    pass  # Mantener valor original si no se puede formatear
        
        # Limpiar campos None
        for key, value in processed.items():
            if value is None:
                processed[key] = ''
        
        return processed
    
    def _process_audit_record_for_export(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un registro de auditoría para exportación."""
        processed = record.copy()
        
        # Formatear timestamp
        if 'timestamp' in processed and processed['timestamp']:
            try:
                dt = datetime.fromisoformat(str(processed['timestamp']).replace('Z', '+00:00'))
                processed['timestamp'] = dt.strftime('%d/%m/%Y %H:%M:%S')
            except:
                pass
        
        # Formatear JSON values para legibilidad
        for json_field in ['old_values', 'new_values']:
            if json_field in processed and processed[json_field]:
                try:
                    import json
                    data = json.loads(processed[json_field])
                    # Convertir a string legible
                    formatted_items: List[str] = []
                    for key, value in data.items():
                        formatted_items.append(f"{key}: {value}")
                    processed[json_field] = "; ".join(formatted_items)
                except:
                    pass  # Mantener valor original
        
        # Limpiar campos None
        for key, value in processed.items():
            if value is None:
                processed[key] = ''
        
        return processed
    
    def _format_dataframe_for_export(self, df: pd.DataFrame) -> pd.DataFrame:
        """Formatea un DataFrame para exportación."""
        df_formatted = df.copy()
        
        # Formatear columnas de fecha
        date_columns = ['Fecha Homologación', 'Fecha Creación', 'Última Actualización']
        for col in date_columns:
            if col in df_formatted.columns:
                df_formatted[col] = pd.to_datetime(df_formatted[col], errors='coerce')
                df_formatted[col] = df_formatted[col].dt.strftime('%d/%m/%Y %H:%M:%S')
        
        # Formatear columna de versiones previas
        if 'Versiones Previas' in df_formatted.columns:
            df_formatted['Versiones Previas'] = df_formatted['Versiones Previas'].map(
                {True: 'Sí', False: 'No', 1: 'Sí', 0: 'No'}
            ).fillna('No')
        
        # Rellenar valores None/NaN
        df_formatted = df_formatted.fillna('')
        
        return df_formatted
    
    def get_export_summary(self, export_type: str, record_count: int, 
                          filename: str) -> Dict[str, Any]:
        """Genera resumen de exportación."""
        return {
            'export_type': export_type,
            'record_count': record_count,
            'filename': os.path.basename(filename),
            'file_size': os.path.getsize(filename) if os.path.exists(filename) else 0,
            'export_timestamp': datetime.now().isoformat(),
            'pandas_available': PANDAS_AVAILABLE
        }


def export_homologations_csv(filename: str, filters: Optional[Dict[str, Any]] = None, 
                           user_id: Optional[int] = None) -> bool:
    """Función utilitaria para exportar homologaciones a CSV."""
    exporter = DataExporter()
    return exporter.export_homologations_to_csv(filename, filters, user_id)


def export_homologations_excel(filename: str, filters: Optional[Dict[str, Any]] = None,
                             user_id: Optional[int] = None) -> bool:
    """Función utilitaria para exportar homologaciones a Excel."""
    exporter = DataExporter()
    return exporter.export_homologations_to_excel(filename, filters, user_id)


def export_audit_trail_csv(filename: str, filters: Optional[Dict[str, Any]] = None,
                          user_id: Optional[int] = None) -> bool:
    """Función utilitaria para exportar trail de auditoría a CSV."""
    exporter = DataExporter()
    return exporter.export_audit_trail_to_csv(filename, filters, user_id)


def generate_filename(base_name: str, extension: str, include_timestamp: bool = True) -> str:
    """Genera nombre de archivo para exportación."""
    if include_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.{extension}"
    else:
        return f"{base_name}.{extension}"


if __name__ == "__main__":
    # Test del sistema de exportación
    from core.settings import setup_logging
    from data.seed import create_seed_data
    
    setup_logging()
    
    print("=== Test del Sistema de Exportación ===")
    
    try:
        # Crear seed data
        create_seed_data()
        
        # Test de exportación
        exporter = DataExporter()
        
        # Generar nombre de archivo de prueba
        test_filename = generate_filename("homologaciones_test", "csv")
        
        print(f"Exportando a: {test_filename}")
        success = exporter.export_homologations_to_csv(test_filename)
        
        if success:
            print("✓ Exportación CSV exitosa")
            
            # Mostrar resumen
            summary = exporter.get_export_summary("CSV", 0, test_filename)
            print(f"Archivo: {summary['filename']}")
            print(f"Tamaño: {summary['file_size']} bytes")
            print(f"Pandas disponible: {summary['pandas_available']}")
        
        # Test de Excel si pandas está disponible
        if PANDAS_AVAILABLE:
            excel_filename = generate_filename("homologaciones_test", "xlsx")
            print(f"\nExportando Excel a: {excel_filename}")
            
            success_excel = exporter.export_homologations_to_excel(excel_filename)
            if success_excel:
                print("✓ Exportación Excel exitosa")
        else:
            print("⚠ Pandas no disponible, omitiendo test de Excel")
        
        print("\n=== Test completado exitosamente ===")
        
    except Exception as e:
        print(f"Error en test: {e}")
        logger.error(f"Error en test: {e}")