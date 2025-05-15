# YouTube Audio Translator (English to Brazilian Portuguese)

Este aplicativo permite baixar o áudio de vídeos do YouTube em inglês, traduzi-los para português do Brasil e manter a mesma duração do áudio original para sincronização perfeita com o vídeo.

## Funcionalidades

- Download de áudio de vídeos do YouTube
- Transcrição do áudio (inglês)
- Tradução do texto (inglês para português do Brasil)
- Sintetização do texto traduzido em áudio
- Ajuste de tempo para manter a sincronização
- Suporte a vídeos longos (divisão em partes)
- Interface web amigável

## Pré-requisitos

- Python 3.11 ou superior
- As bibliotecas listadas em `dependencies.txt`

## Instalação

1. Clone o repositório
2. Instale as dependências:
   ```
   pip install -r dependencies.txt
   ```

## Uso

1. Execute o servidor:
   ```
   python main.py
   ```
   ou
   ```
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

2. Acesse a aplicação no navegador: http://localhost:5000

3. Cole a URL de um vídeo do YouTube em inglês e clique em "Traduzir"

4. Aguarde o processamento e baixe o áudio traduzido quando estiver pronto

## Estrutura do Projeto

- `main.py` - Ponto de entrada da aplicação
- `app.py` - Configuração do Flask e rotas do aplicativo
- `yt_translator.py` - Gerenciamento de jobs e download de áudio do YouTube
- `audio_processor.py` - Processamento de áudio (transcrição, tradução, síntese)
- `templates/` - Arquivos HTML da interface web
  - `layout.html` - Template base com CSS e JavaScript
  - `index.html` - Página inicial com formulário
  - `result.html` - Página de resultado e download
- `static/` - Arquivos estáticos
  - `app.js` - JavaScript para atualização automática da página
  - `custom.css` - Estilos personalizados

## Observações

Para uma implementação completa, é necessário configurar:

1. Google Cloud Speech-to-Text para transcrição
2. Google Cloud Translation para tradução
3. Google Cloud Text-to-Speech para sintetização

A versão atual usa implementações simuladas dessas funcionalidades para fins de demonstração.

## Implementação em Produção

Para usar este aplicativo com APIs reais, você precisará:

1. Criar uma conta no Google Cloud Platform
2. Ativar as APIs: Speech-to-Text, Cloud Translation e Text-to-Speech
3. Criar chaves de API e configurar as credenciais
4. Atualizar as classes AudioProcessor e YouTubeTranslator para usar as APIs reais