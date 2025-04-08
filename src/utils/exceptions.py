"""カスタム例外定義"""

class AnypointError(Exception):
    """Anypoint Platform関連の基本例外クラス"""
    pass

class ConfigurationError(AnypointError):
    """設定関連のエラー"""
    pass

class AuthenticationError(AnypointError):
    """認証関連のエラー"""
    pass

class APIError(AnypointError):
    """API呼び出し関連のエラー"""
    pass
