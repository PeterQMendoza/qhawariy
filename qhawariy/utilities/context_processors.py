from flask import g


def inject_nonce():
    """Injecta un procesador de contexto para que la variable"""
    return {'nonce': getattr(g, 'nonce', '')}
