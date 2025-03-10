springboot 中是如何加载和传递全局配置和库配置的？
--- R1
在 Spring Boot 中，全局配置和库配置的加载与传递通过以下分层机制实现，遵循 **「约定大于配置」** 原则：

---

### 一、配置加载机制（层级优先级从高到低）

| 配置源                        | 说明                                                            |
| ----------------------------- | --------------------------------------------------------------- |
| **命令行参数**                | `java -jar app.jar --server.port=8081`                          |
| **操作系统环境变量**          | `export SPRING_DATASOURCE_URL=jdbc:mysql://localhost:3306/mydb` |
| **application-{profile}.yml** | Profile 专属配置（如 `application-prod.yml`）                   |
| **application.yml**           | 主配置文件（支持 YAML 层级结构）                                |
| **@Configuration 代码配置**   | 通过 `@Bean` 定义的 Java Config                                 |

---

### 二、全局配置管理（以 MySQL + JPA 为例）

#### 1. 配置文件示例 (`application.yml`)

```yaml
# 全局服务配置
server:
  port: 8080
  servlet:
    context-path: /api

# 数据源配置（库配置）
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useSSL=false
    username: root
    password: securepassword
    driver-class-name: com.mysql.cj.jdbc.Driver

  # JPA 配置（库配置）
  jpa:
    show-sql: true
    hibernate:
      ddl-auto: update
    properties:
      hibernate:
        format_sql: true
```

#### 2. 配置注入方式

**方式一：`@Value` 直接注入**

```java
@Service
public class OrderService {
    @Value("${server.servlet.context-path}")
    private String apiBasePath;

    @Value("${spring.datasource.url}")
    private String dbUrl;
}
```

**方式二：类型安全绑定 (`@ConfigurationProperties`)**

```java
@Configuration
@ConfigurationProperties(prefix = "spring.datasource")
public class DataSourceConfig {
    private String url;
    private String username;
    private String password;

    // Getter/Setter 必需
}
```

---

### 三、第三方库配置集成

#### 1. 自动配置原理

Spring Boot Starter 通过 `spring-boot-autoconfigure` 实现 **「条件装配」**：

```java
@Configuration
@ConditionalOnClass({DataSource.class, EmbeddedDatabaseType.class})
@EnableConfigurationProperties(DataSourceProperties.class)
public class DataSourceAutoConfiguration {
    @Bean
    @ConditionalOnMissingBean
    public DataSource dataSource(DataSourceProperties properties) {
        return properties.initializeDataSourceBuilder().build();
    }
}
```

#### 2. 自定义库配置（以 Redis 为例）

**① 添加依赖 (`pom.xml`)**

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

**② 配置参数 (`application.yml`)**

```yaml
spring:
  redis:
    host: redis.example.com
    port: 6379
    password: redispwd
    database: 0
```

**③ 自动注入使用**

```java
@Autowired
private RedisTemplate<String, Object> redisTemplate;
```

---

### 四、多环境配置策略

#### 1. Profile 专属配置

| 文件名                 | 激活方式                                   |
| ---------------------- | ------------------------------------------ |
| `application-dev.yml`  | `spring.profiles.active=dev`               |
| `application-test.yml` | 通过 `@ActiveProfiles("test")`             |
| `application-prod.yml` | 命令行参数 `--spring.profiles.active=prod` |

#### 2. 动态配置示例

```java
@Profile("dev")
@Configuration
public class DevConfig {
    @Bean
    public MyService mockService() {
        return new MockService();
    }
}
```

---

### 五、最佳实践建议

1. **优先使用 YAML**  
   YAML 的层级结构比 Properties 文件更清晰，适合复杂配置

2. **敏感信息加密**  
   使用 `jasypt` 对密码等敏感配置加密：

   ```yaml
   spring:
     datasource:
       password: ENC(密文)
   ```

3. **外部化配置**  
   生产环境通过 Kubernetes ConfigMap 或 `bootstrap.yml` 覆盖配置

4. **配置校验**  
   通过 `@Validated` 校验配置合法性：
   ```java
   @ConfigurationProperties(prefix = "app")
   @Validated
   public class AppConfig {
       @NotNull
       private String version;
   }
   ```

---

通过这种分层配置体系，Spring Boot 实现了 **「配置即代码」** 的理念，使全局配置和库配置的管理变得灵活且类型安全。
