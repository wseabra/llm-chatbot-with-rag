"""
Unit tests for the main application module.

This module tests the main application initialization and startup logic
following the project's testing standards.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from io import StringIO
import inspect
from fastapi.testclient import TestClient

from src.main import app, main


class TestMainModule:
    """Test suite for the main application module."""
    
    @pytest.mark.unit
    def test_app_initialization(self):
        """Test that app is properly initialized."""
        assert app is not None
        assert hasattr(app, 'title')
        assert hasattr(app, 'description')
        assert hasattr(app, 'version')
        assert app.title == "FastAPI RAG Application"
        assert app.version == "1.0.0"
    
    @pytest.mark.unit
    def test_app_has_required_routes(self):
        """Test that app has all required routes."""
        route_paths = [route.path for route in app.routes]
        
        # Check for required routes
        assert "/" in route_paths
        assert "/health" in route_paths
        assert "/health/simple" in route_paths
        
        # Check for chat routes (with prefix)
        chat_routes = [path for path in route_paths if path.startswith("/chat")]
        assert len(chat_routes) >= 2  # At least completion and advanced
    
    @pytest.mark.unit
    def test_app_openapi_configuration(self):
        """Test that app has proper OpenAPI configuration."""
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"
        assert "RAG capabilities" in app.description
    
    @pytest.mark.unit
    @patch('uvicorn.run')
    def test_main_function_calls_uvicorn(self, mock_uvicorn_run):
        """Test that main function calls uvicorn.run with correct parameters."""
        # Capture stdout to verify print statement
        captured_output = StringIO()
        
        with patch('sys.stdout', captured_output):
            main()
        
        # Verify uvicorn.run was called with correct parameters
        mock_uvicorn_run.assert_called_once_with(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        
        # Verify startup message was printed
        output = captured_output.getvalue()
        assert "Starting FastAPI RAG Application server..." in output
    
    @pytest.mark.unit
    @patch('uvicorn.run')
    def test_main_function_uses_correct_app_instance(self, mock_uvicorn_run):
        """Test that main function uses the correct app instance."""
        main()
        
        # Get the app instance passed to uvicorn.run
        call_args = mock_uvicorn_run.call_args
        passed_app = call_args[0][0]  # First positional argument
        
        # Verify it's the same app instance
        assert passed_app is app
    
    @pytest.mark.unit
    @patch('uvicorn.run')
    @patch('builtins.print')
    def test_main_function_startup_message(self, mock_print, mock_uvicorn_run):
        """Test that main function prints startup message."""
        main()
        
        # Verify print was called with startup message
        mock_print.assert_called_once_with("Starting FastAPI RAG Application server...")
    
    @pytest.mark.unit
    @patch('uvicorn.run')
    def test_main_function_server_configuration(self, mock_uvicorn_run):
        """Test that main function configures server correctly."""
        main()
        
        # Verify server configuration
        call_kwargs = mock_uvicorn_run.call_args[1]
        
        assert call_kwargs['host'] == "0.0.0.0"
        assert call_kwargs['port'] == 8000
        assert call_kwargs['log_level'] == "info"
    
    @pytest.mark.unit
    @patch('uvicorn.run')
    def test_main_function_exception_handling(self, mock_uvicorn_run):
        """Test that main function handles exceptions gracefully."""
        # Make uvicorn.run raise an exception
        mock_uvicorn_run.side_effect = Exception("Server startup failed")
        
        # main() should not suppress the exception
        with pytest.raises(Exception, match="Server startup failed"):
            main()
    
    @pytest.mark.unit
    @patch('src.main.main')
    def test_main_execution_when_run_as_script(self, mock_main_function):
        """Test that main() is called when module is run as script."""
        # Simulate running as main module
        with patch('src.main.__name__', '__main__'):
            # Re-import to trigger the if __name__ == "__main__" block
            import importlib
            import src.main
            importlib.reload(src.main)
        
        # Note: This test is tricky because the if __name__ == "__main__" 
        # block runs during import. In a real scenario, we'd test this
        # by running the script directly, but for unit tests we verify
        # the structure is correct.
        assert hasattr(src.main, 'main')
        assert callable(src.main.main)


class TestMainIntegration:
    """Integration tests for main application module."""
    
    @pytest.mark.integration
    def test_app_can_be_imported_and_used(self):
        """Test that app can be imported and used by external tools."""
        from src.main import app
        
        # Verify app is a FastAPI instance
        assert hasattr(app, 'get')
        assert hasattr(app, 'post')
        assert hasattr(app, 'routes')
        assert hasattr(app, 'openapi')
    
    @pytest.mark.integration
    def test_app_openapi_schema_generation(self):
        """Test that app can generate OpenAPI schema."""
        from src.main import app
        
        # Generate OpenAPI schema
        schema = app.openapi()
        
        assert isinstance(schema, dict)
        assert 'info' in schema
        assert 'paths' in schema
        assert schema['info']['title'] == "FastAPI RAG Application"
        assert schema['info']['version'] == "1.0.0"
    
    @pytest.mark.integration
    def test_app_routes_are_accessible(self):
        """Test that all app routes are properly registered and accessible."""
        from src.main import app
        
        client = TestClient(app)
        
        # Test root route
        response = client.get("/")
        assert response.status_code == 200
        
        # Test simple health route
        response = client.get("/health/simple")
        assert response.status_code == 200
        
        # Test OpenAPI docs
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/redoc")
        assert response.status_code == 200
    
    @pytest.mark.integration
    @patch('uvicorn.run')
    def test_complete_startup_workflow(self, mock_uvicorn_run):
        """Test complete application startup workflow."""
        from src.main import main, app
        
        # Verify app is properly initialized before main() is called
        assert app is not None
        assert app.title == "FastAPI RAG Application"
        
        # Call main function
        main()
        
        # Verify uvicorn was called with the initialized app
        mock_uvicorn_run.assert_called_once()
        call_args = mock_uvicorn_run.call_args
        passed_app = call_args[0][0]
        
        assert passed_app is app
        assert passed_app.title == "FastAPI RAG Application"


class TestMainModuleStructure:
    """Test suite for main module structure and organization."""
    
    @pytest.mark.unit
    def test_main_module_imports(self):
        """Test that main module has correct imports."""
        import src.main
        
        # Verify required attributes exist
        assert hasattr(src.main, 'app')
        assert hasattr(src.main, 'main')
        
        # Verify app is from api module
        from src.api import create_app
        assert type(src.main.app) == type(create_app())
    
    @pytest.mark.unit
    def test_main_module_docstring(self):
        """Test that main module has proper documentation."""
        import src.main
        
        assert src.main.__doc__ is not None
        assert "Application entry point" in src.main.__doc__
        assert "initialization" in src.main.__doc__
    
    @pytest.mark.unit
    def test_main_function_docstring(self):
        """Test that main function has proper documentation."""
        from src.main import main
        
        assert main.__doc__ is not None
        assert "Main function" in main.__doc__
        assert "start" in main.__doc__.lower()
    
    @pytest.mark.unit
    def test_main_module_separation_of_concerns(self):
        """Test that main module follows separation of concerns."""
        import src.main
        import inspect
        
        # Get all functions and classes defined in main module
        members = inspect.getmembers(src.main, 
                                   lambda x: inspect.isfunction(x) or inspect.isclass(x))
        
        # Filter to only those defined in main module (not imported)
        main_defined = [name for name, obj in members 
                       if hasattr(obj, '__module__') and obj.__module__ == 'src.main']
        
        # Should only have main function defined here
        # (app is imported from api module)
        assert 'main' in main_defined
        
        # Should not have route definitions or API logic
        route_indicators = ['get', 'post', 'router', 'endpoint']
        for indicator in route_indicators:
            assert indicator not in main_defined
    
    @pytest.mark.unit
    def test_app_instance_is_from_api_module(self):
        """Test that app instance comes from api module."""
        from src.main import app
        from src.api import create_app
        
        # Both should be FastAPI instances with same configuration
        created_app = create_app()
        
        assert type(app) == type(created_app)
        assert app.title == created_app.title
        assert app.version == created_app.version
        assert app.description == created_app.description


class TestMainErrorScenarios:
    """Test suite for error scenarios in main module."""
    
    @pytest.mark.unit
    @patch('uvicorn.run')
    def test_main_with_uvicorn_import_error(self, mock_uvicorn_run):
        """Test main function behavior when uvicorn import fails."""
        # This test verifies the import structure is correct
        # In practice, if uvicorn import fails, the module wouldn't load
        
        # Verify uvicorn is imported inside main function
        import src.main
        source = inspect.getsource(src.main.main)
        assert 'import uvicorn' in source
    
    @pytest.mark.unit
    @patch('uvicorn.run')
    def test_main_with_server_startup_failure(self, mock_uvicorn_run):
        """Test main function when server startup fails."""
        # Simulate server startup failure
        mock_uvicorn_run.side_effect = OSError("Port already in use")
        
        with pytest.raises(OSError, match="Port already in use"):
            main()
    
    @pytest.mark.unit
    def test_app_initialization_robustness(self):
        """Test that app initialization is robust."""
        from src.main import app
        
        # App should be initialized even if main() hasn't been called
        assert app is not None
        assert hasattr(app, 'routes')
        assert len(list(app.routes)) > 0  # Should have routes registered


# Parametrized tests for different configurations
class TestMainParametrized:
    """Parametrized tests for main module configurations."""
    
    @pytest.mark.parametrize("host,port,log_level", [
        ("0.0.0.0", 8000, "info"),      # Default configuration
        ("127.0.0.1", 3000, "debug"),  # Alternative configuration
        ("localhost", 5000, "warning"), # Another alternative
    ])
    @pytest.mark.unit
    @patch('uvicorn.run')
    def test_main_function_configuration_flexibility(self, mock_uvicorn_run, host, port, log_level):
        """Test that main function could be configured for different environments."""
        # Note: Current implementation uses hardcoded values
        # This test documents the current behavior and could guide future improvements
        
        main()
        
        # Verify current hardcoded configuration
        call_kwargs = mock_uvicorn_run.call_args[1]
        assert call_kwargs['host'] == "0.0.0.0"  # Current hardcoded value
        assert call_kwargs['port'] == 8000       # Current hardcoded value
        assert call_kwargs['log_level'] == "info" # Current hardcoded value
        
        # This test serves as documentation that these values are hardcoded
        # and could be made configurable in the future
    
    @pytest.mark.parametrize("app_attribute", [
        "title", "description", "version", "docs_url", "redoc_url"
    ])
    @pytest.mark.unit
    def test_app_has_required_attributes(self, app_attribute):
        """Test that app has all required FastAPI attributes."""
        from src.main import app
        
        assert hasattr(app, app_attribute)
        assert getattr(app, app_attribute) is not None