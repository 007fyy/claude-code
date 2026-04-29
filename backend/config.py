from pydantic_settings import BaseSettings
# 这个文件的作用是定义应用程序的配置和业务错误类。Settings类使用Pydantic库来定义应用程序的配置项，包括数据库连接URL、JWT密钥、JWT过期时间、调试模式以及邮件服务器配置。通过从环境变量加载这些配置项，可以方便地在不同环境中进行配置管理。BizError类是一个自定义的异常类，用于表示业务逻辑中的错误，包含错误码和错误信息，便于在应用程序中统一处理错误情况。

class Settings(BaseSettings):
    # 数据库连接URL，使用MySQL数据库，用户名为root，密码为空，主机地址为127.0.0.1，端口为3306，数据库名称为longshi，字符集为utf8mb4
    DATABASE_URL: str = "mysql+pymysql://root@127.0.0.1:3306/longshi?charset=utf8mb4"
    # JWT密钥，用于生成和验证JWT令牌，生产环境中应该更改为一个安全的值
    JWT_SECRET: str = "longshi-dev-secret-change-in-prod"
    # JWT令牌过期时间，单位为分钟，这里设置为7天
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天
    # 调试模式，默认为True，生产环境中应该设置为False
    DEBUG: bool = True

    # QQ 邮箱 SMTP 配置（留空则退回 mock 模式，验证码打印到控制台）
    # 注释：QQ邮箱验证码，就用465端口，使用SSL连接
    EMAIL_HOST: str = "smtp.qq.com"
    EMAIL_PORT: int = 465
    EMAIL_USER: str = "2324903027@qq.com"       # 你的 QQ 邮箱，如 123456789@qq.com
    EMAIL_PASSWORD: str = "sktjebqtzdjqdifi"   # QQ 邮箱授权码（非登录密码，在 QQ 邮箱设置→账户→开启SMTP获取）
    # 注释：QQ邮箱验证码， --- IGNORE ---
    class Config:
        env_file = ".env"


settings = Settings()

# 业务错误类，包含错误码和错误信息
class BizError(Exception):
    def __init__(self, code: int, message: str):
        # code: 业务错误码，message: 错误信息
        self.code = code
        self.message = message
