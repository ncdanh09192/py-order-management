import pytest
from datetime import timedelta
from unittest.mock import patch, Mock
from jose import JWTError
from fastapi import HTTPException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token
)


class TestSecurity:
    """Test cases for security module"""
    
    @pytest.fixture
    def sample_data(self):
        return {"sub": "123", "customer_id": 123}
    
    @pytest.fixture
    def custom_expires_delta(self):
        return timedelta(hours=2)
    
    def test_create_access_token_default_expiry(self, sample_data):
        """Test access token creation with default expiry"""
        with patch('app.core.security.settings') as mock_settings, \
             patch('app.core.security.datetime') as mock_datetime, \
             patch('app.core.security.jwt.encode') as mock_encode:
            
            mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
            mock_datetime.utcnow.return_value = Mock()
            mock_datetime.utcnow.return_value.__add__ = Mock(return_value=Mock())
            mock_encode.return_value = "encoded_token"
            
            result = create_access_token(sample_data)
            
            assert result == "encoded_token"
            mock_encode.assert_called_once()
            
            # Verify the call arguments
            call_args = mock_encode.call_args
            assert call_args[0][0]["sub"] == "123"
            assert call_args[0][0]["customer_id"] == 123
            assert call_args[0][0]["type"] == "access"
            assert "exp" in call_args[0][0]
    
    def test_create_access_token_custom_expiry(self, sample_data, custom_expires_delta):
        """Test access token creation with custom expiry"""
        with patch('app.core.security.datetime') as mock_datetime, \
             patch('app.core.security.jwt.encode') as mock_encode:
            
            mock_datetime.utcnow.return_value = Mock()
            mock_datetime.utcnow.return_value.__add__ = Mock(return_value=Mock())
            mock_encode.return_value = "encoded_token"
            
            result = create_access_token(sample_data, custom_expires_delta)
            
            assert result == "encoded_token"
            mock_encode.assert_called_once()
    
    def test_create_refresh_token_default_expiry(self, sample_data):
        """Test refresh token creation with default expiry"""
        with patch('app.core.security.settings') as mock_settings, \
             patch('app.core.security.datetime') as mock_datetime, \
             patch('app.core.security.jwt.encode') as mock_encode:
            
            mock_settings.REFRESH_TOKEN_EXPIRE_DAYS = 7
            mock_datetime.utcnow.return_value = Mock()
            mock_datetime.utcnow.return_value.__add__ = Mock(return_value=Mock())
            mock_encode.return_value = "encoded_refresh_token"
            
            result = create_refresh_token(sample_data)
            
            assert result == "encoded_refresh_token"
            mock_encode.assert_called_once()
            
            # Verify the call arguments
            call_args = mock_encode.call_args
            assert call_args[0][0]["sub"] == "123"
            assert call_args[0][0]["customer_id"] == 123
            assert call_args[0][0]["type"] == "refresh"
            assert "exp" in call_args[0][0]
    
    def test_verify_access_token_success(self, sample_data):
        """Test successful access token verification"""
        with patch('app.core.security.jwt.decode') as mock_decode, \
             patch('app.core.security.settings') as mock_settings:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_decode.return_value = {**sample_data, "type": "access"}
            
            result = verify_access_token("valid_token")
            
            assert result == {**sample_data, "type": "access"}
            mock_decode.assert_called_once_with(
                "valid_token", 
                "test_secret", 
                algorithms=["HS256"]
            )
    
    def test_verify_access_token_invalid_type(self, sample_data):
        """Test access token verification with invalid type"""
        with patch('app.core.security.jwt.decode') as mock_decode, \
             patch('app.core.security.settings') as mock_settings:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_decode.return_value = {**sample_data, "type": "refresh"}  # Wrong type
            
            with pytest.raises(HTTPException) as exc_info:
                verify_access_token("invalid_type_token")
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid token type"
    
    def test_verify_access_token_jwt_error(self, sample_data):
        """Test access token verification with JWT decode error"""
        with patch('app.core.security.jwt.decode') as mock_decode, \
             patch('app.core.security.settings') as mock_settings:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_decode.side_effect = JWTError("Invalid token")
            
            with pytest.raises(HTTPException) as exc_info:
                verify_access_token("invalid_token")
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Could not validate credentials"
    
    def test_verify_refresh_token_success(self, sample_data):
        """Test successful refresh token verification"""
        with patch('app.core.security.jwt.decode') as mock_decode, \
             patch('app.core.security.settings') as mock_settings:
            
            mock_settings.REFRESH_SECRET_KEY = "test_refresh_secret"
            mock_decode.return_value = {**sample_data, "type": "refresh"}
            
            result = verify_refresh_token("valid_refresh_token")
            
            assert result == {**sample_data, "type": "refresh"}
            mock_decode.assert_called_once_with(
                "valid_refresh_token", 
                "test_refresh_secret", 
                algorithms=["HS256"]
            )
    
    def test_verify_refresh_token_invalid_type(self, sample_data):
        """Test refresh token verification with invalid type"""
        with patch('app.core.security.jwt.decode') as mock_decode, \
             patch('app.core.security.settings') as mock_settings:
            
            mock_settings.REFRESH_SECRET_KEY = "test_refresh_secret"
            mock_decode.return_value = {**sample_data, "type": "access"}  # Wrong type
            
            with pytest.raises(HTTPException) as exc_info:
                verify_refresh_token("invalid_type_refresh_token")
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid token type"
    
    def test_verify_refresh_token_jwt_error(self, sample_data):
        """Test refresh token verification with JWT decode error"""
        with patch('app.core.security.jwt.decode') as mock_decode, \
             patch('app.core.security.settings') as mock_settings:
            
            mock_settings.REFRESH_SECRET_KEY = "test_refresh_secret"
            mock_decode.side_effect = JWTError("Invalid refresh token")
            
            with pytest.raises(HTTPException) as exc_info:
                verify_refresh_token("invalid_refresh_token")
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Could not validate refresh token"
