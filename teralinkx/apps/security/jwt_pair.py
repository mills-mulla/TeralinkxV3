# apps/security/jwt_pair.py
from rest_framework_simplejwt.tokens import RefreshToken
from .querycheckout import JWTClaimsEnhancer

class JWTTokens:
    """
    Generate JWT tokens with custom claims
    """
    
    @staticmethod
    def generate_token_pair(user):
        """
        Generate access and refresh tokens with custom claims
        
        Args:
            user: Django User instance
            
        Returns:
            dict: {'access': '...', 'refresh': '...', 'user': {...}}
        """
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims
        custom_claims = JWTClaimsEnhancer.get_user_claims_for_jwt(user)
        for key, value in custom_claims.items():
            if value is not None:
                refresh[key] = value
        
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'account': custom_claims.get('client_account'),
                'account_tier': custom_claims.get('account_tier'),
                'balance': custom_claims.get('balance'),
            }
        }
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """
        Refresh access token while preserving custom claims
        """
        try:
            token = RefreshToken(refresh_token)
            user_id = token.get('user_id')
            
            if user_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)
                
                # Regenerate custom claims
                custom_claims = JWTClaimsEnhancer.get_user_claims_for_jwt(user)
                for key, value in custom_claims.items():
                    if value is not None:
                        token[key] = value
                
                return {
                    'access': str(token.access_token),
                    'refresh': str(token),
                }
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise