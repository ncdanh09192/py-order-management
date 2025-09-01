import pytest
from unittest.mock import Mock, patch
from app.services.auth_service import AuthService
from app.dto.requests.auth_request import LoginTestRequest, RefreshTokenRequest
from app.dto.responses.auth_response import LoginTestResponse, TokenResponse


class TestAuthService:
    """Test cases for AuthService"""
    
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    @pytest.fixture
    def valid_login_request(self):
        return LoginTestRequest(customer_id=123)
    
    @pytest.fixture
    def invalid_login_request(self):
        return LoginTestRequest(customer_id=0)
    
    @pytest.fixture
    def negative_login_request(self):
        return LoginTestRequest(customer_id=-1)
    
    @pytest.fixture
    def valid_refresh_request(self):
        return RefreshTokenRequest(refresh_token="valid_refresh_token")
    
    @pytest.mark.asyncio
    async def test_login_test_success(self, auth_service, valid_login_request):
        """Test successful login test"""
        with patch('app.services.auth_service.create_access_token') as mock_access, \
             patch('app.services.auth_service.create_refresh_token') as mock_refresh:
            
            mock_access.return_value = "access_token_123"
            mock_refresh.return_value = "refresh_token_123"
            
            result = await auth_service.login_test(valid_login_request)
            
            assert isinstance(result, LoginTestResponse)
            assert result.access_token == "access_token_123"
            assert result.refresh_token == "refresh_token_123"
            assert result.token_type == "bearer"
            assert result.expires_in == 1800
            assert result.customer_id == 123
            
            # Verify token creation calls
            mock_access.assert_called_once_with(
                data={"sub": "123", "customer_id": 123}
            )
            mock_refresh.assert_called_once_with(
                data={"sub": "123", "customer_id": 123}
            )
    
    @pytest.mark.asyncio
    async def test_login_test_invalid_customer_id_zero(self, auth_service, invalid_login_request):
        """Test login test with customer_id = 0"""
        with pytest.raises(ValueError, match="Invalid customer ID"):
            await auth_service.login_test(invalid_login_request)
    
    @pytest.mark.asyncio
    async def test_login_test_invalid_customer_id_negative(self, auth_service, negative_login_request):
        """Test login test with negative customer_id"""
        with pytest.raises(ValueError, match="Invalid customer ID"):
            await auth_service.login_test(negative_login_request)
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, auth_service, valid_refresh_request):
        """Test successful token refresh"""
        with patch('app.core.security.verify_refresh_token') as mock_verify, \
             patch('app.services.auth_service.create_access_token') as mock_access, \
             patch('app.services.auth_service.create_refresh_token') as mock_refresh:
            
            mock_verify.return_value = {"customer_id": 123}
            mock_access.return_value = "new_access_token_123"
            mock_refresh.return_value = "new_refresh_token_123"
            
            result = await auth_service.refresh_token(valid_refresh_request)
            
            assert isinstance(result, TokenResponse)
            assert result.access_token == "new_access_token_123"
            assert result.refresh_token == "new_refresh_token_123"
            assert result.token_type == "bearer"
            assert result.expires_in == 1800
            
            # Verify calls
            mock_verify.assert_called_once_with("valid_refresh_token")
            mock_access.assert_called_once_with(
                data={"sub": "123", "customer_id": 123}
            )
            mock_refresh.assert_called_once_with(
                data={"sub": "123", "customer_id": 123}
            )
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid_payload(self, auth_service, valid_refresh_request):
        """Test token refresh with invalid payload"""
        with patch('app.core.security.verify_refresh_token') as mock_verify:
            mock_verify.return_value = {}  # No customer_id in payload
            
            with pytest.raises(ValueError, match="Invalid refresh token payload"):
                await auth_service.refresh_token(valid_refresh_request)
    
    @pytest.mark.asyncio
    async def test_refresh_token_verification_failure(self, auth_service, valid_refresh_request):
        """Test token refresh when verification fails"""
        with patch('app.core.security.verify_refresh_token') as mock_verify:
            mock_verify.side_effect = ValueError("Invalid token")
            
            with pytest.raises(ValueError, match="Invalid token"):
                await auth_service.refresh_token(valid_refresh_request)
