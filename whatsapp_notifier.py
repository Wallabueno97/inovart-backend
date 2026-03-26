import logging
from typing import Dict

logger = logging.getLogger(__name__)

ADMIN_WHATSAPP = "5569993954448"  # WhatsApp do admin para notificações INOVART3D

def send_whatsapp_notification(appointment_data: Dict) -> bool:
    """
    Simula envio de notificação via WhatsApp
    Em produção, integrar com API do WhatsApp Business ou Twilio
    """
    try:
        message = f"""
🔔 NOVO AGENDAMENTO - INOVART3D

👤 Cliente: {appointment_data.get('customerName')}
📞 Telefone: {appointment_data.get('customerPhone')}
📧 Email: {appointment_data.get('customerEmail', 'Não informado')}

🖨️ Serviço: {appointment_data.get('serviceName')}
📅 Data Preferida: {appointment_data.get('preferredDate')}
🕐 Horário: {appointment_data.get('preferredTime')}

📝 Projeto: {appointment_data.get('motorcycleModel', 'Não informado')}
💬 Observações: {appointment_data.get('notes', 'Nenhuma')}

Acesse o painel administrativo para confirmar o agendamento.
        """
        
        # Log da mensagem que seria enviada
        logger.info(f"WhatsApp notification to {ADMIN_WHATSAPP}:")
        logger.info(message)
        
        # Em produção, usar API do WhatsApp aqui:
        # whatsapp_api.send_message(to=ADMIN_WHATSAPP, message=message)
        
        return True
    except Exception as e:
        logger.error(f"Error sending WhatsApp notification: {e}")
        return False

def generate_whatsapp_link(phone: str, message: str) -> str:
    """Gera link para WhatsApp com mensagem pré-preenchida"""
    encoded_message = message.replace(" ", "%20").replace("\n", "%0A")
    return f"https://wa.me/{phone}?text={encoded_message}"
