from django.utils import timezone
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SessionCleanupMiddleware:
    """
    Middleware simple para forzar logout al cambiar de día.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verificar si el usuario está autenticado
        if request.user.is_authenticated:
            self.check_daily_logout(request)
        
        response = self.get_response(request)
        return response
    
    def check_daily_logout(self, request):
        """
        Fuerza el logout si es un nuevo día y la sesión es del día anterior.
        """
        session = request.session
        last_activity = session.get('last_activity_date')
        today = timezone.now().date()
        
        if last_activity:
            try:
                last_activity_date = datetime.fromisoformat(last_activity).date()
                
                # Si la última actividad fue en un día anterior, cerrar sesión
                if last_activity_date < today:
                    session.flush()
                    logger.info(f"Usuario {request.user.username} desconectado por cambio de día")
                    return
            except (ValueError, TypeError):
                # Si hay error en el formato de fecha, limpiar y continuar
                session.pop('last_activity_date', None)
        
        # Actualizar fecha de última actividad
        session['last_activity_date'] = today.isoformat()
