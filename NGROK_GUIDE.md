# 🌐 Como usar o sistema com ngrok

O Django está configurado para aceitar conexões externas via ngrok. Siga os passos abaixo:

## 🚀 Configuração rápida

### 1. Instalar ngrok
```bash
# macOS (via Homebrew)
brew install ngrok

# Ou baixar de https://ngrok.com/download
```

### 2. Executar ngrok
```bash
# Em um terminal separado, executar:
ngrok http 8000
```

### 3. Copiar a URL
O ngrok vai mostrar algo como:
```
Forwarding    https://abc123.ngrok-free.app -> http://localhost:8000
```

### 4. Testar acesso
- ✅ **Funcionará**: `https://abc123.ngrok-free.app` 
- ✅ **Seu amigo pode acessar**: A mesma URL de qualquer lugar
- 🔐 **Admin**: `https://abc123.ngrok-free.app/admin/` (admin/admin123)

## ⚙️ Configurações Django aplicadas

O sistema já está configurado com:
- ✅ `ALLOWED_HOSTS = ['*']` - Aceita qualquer host
- ✅ `CSRF_COOKIE_SECURE = False` - Permite requests via ngrok  
- ✅ `CSRF_COOKIE_SAMESITE = None` - Compatível com proxy

## 🐛 Problemas comuns

### Erro 400 "Invalid HTTP_HOST header"
- ✅ **Resolvido**: Django configurado para aceitar qualquer host

### Erro CSRF verification failed
- ✅ **Resolvido**: CSRF configurado para desenvolvimento

### Ngrok mostra "Only for paid plans"
- 🔄 **Solução**: Use URLs https:// (gratuitas no ngrok)

## 🎯 URLs de exemplo

Com ngrok rodando em `https://abc123.ngrok-free.app`:

- **Home**: https://abc123.ngrok-free.app/
- **Dashboard**: https://abc123.ngrok-free.app/dashboard/
- **Agendamentos**: https://abc123.ngrok-free.app/agendamentos/
- **Relatórios**: https://abc123.ngrok-free.app/relatorios/
- **Admin**: https://abc123.ngrok-free.app/admin/

## 💡 Dicas

1. **URLs mudam**: Ngrok gera URLs novas a cada execução (versão gratuita)
2. **HTTPS preferível**: Algumas funcionalidades só funcionam com HTTPS
3. **Performance**: Pode ter latência extra via ngrok
4. **Segurança**: Só para desenvolvimento - não usar em produção

---

🚀 **Sistema pronto para acesso externo via ngrok!**