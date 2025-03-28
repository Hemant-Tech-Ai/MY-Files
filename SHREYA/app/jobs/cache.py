"""
Cache module for Quiz Master application.
Implements caching functionality to improve application performance.
"""
from flask import current_app
from flask_caching import Cache
from functools import wraps
import hashlib
import json

# Initialize cache
cache = Cache()

def init_cache(app):
    """Initialize the cache with the Flask app"""
    # Configure cache
    cache_config = {
        'CACHE_TYPE': app.config.get('CACHE_TYPE', 'simple'),
        'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_TIMEOUT', 300)  # 5 minutes default
    }
    
    # If Redis is configured, use it
    if app.config.get('CACHE_REDIS_URL'):
        cache_config.update({
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_URL': app.config.get('CACHE_REDIS_URL')
        })
    
    cache.init_app(app, config=cache_config)
    app.logger.info(f"Cache initialized with type: {cache_config['CACHE_TYPE']}")

def cached_route(timeout=300):
    """Decorator for caching API routes with dynamic keys based on request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get current app
            app = current_app._get_current_object()
            
            # Skip caching if disabled
            if not app.config.get('ENABLE_CACHING', True):
                return f(*args, **kwargs)
            
            # Create cache key from function name, args, kwargs, and request data
            from flask import request
            
            # Start with function info
            key_parts = [f.__module__, f.__name__]
            
            # Add args and kwargs
            for arg in args:
                if hasattr(arg, '__dict__'):
                    key_parts.append(str(arg.__dict__))
                else:
                    key_parts.append(str(arg))
            
            for k, v in kwargs.items():
                key_parts.append(f"{k}={v}")
            
            # Add request info if available
            if request:
                if request.args:
                    key_parts.append(str(request.args))
                
                if request.get_json(silent=True):
                    key_parts.append(json.dumps(request.get_json(), sort_keys=True))
                
                # Add auth user if available
                from flask_jwt_extended import get_jwt_identity
                try:
                    user = get_jwt_identity()
                    if user:
                        key_parts.append(f"user={user}")
                except:
                    pass
            
            # Create hash of all parts
            key_str = '_'.join(key_parts)
            cache_key = hashlib.md5(key_str.encode()).hexdigest()
            
            # Get from cache
            rv = cache.get(cache_key)
            if rv is not None:
                app.logger.debug(f"Cache hit for {f.__name__}")
                return rv
            
            # Generate new response
            app.logger.debug(f"Cache miss for {f.__name__}")
            rv = f(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, rv, timeout=timeout)
            return rv
            
        return decorated_function
    return decorator

def invalidate_user_cache(user_id):
    """Invalidate all cache entries related to a specific user"""
    # This is a simple implementation that clears the entire cache
    # In a production environment, you would want to be more selective
    cache.clear()

def invalidate_quiz_cache(quiz_id):
    """Invalidate all cache entries related to a specific quiz"""
    # This is a simple implementation that clears the entire cache
    # In a production environment, you would want to be more selective
    cache.clear()

def invalidate_all_cache():
    """Invalidate all cache entries"""
    cache.clear() 