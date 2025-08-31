# Gemini MCP Server

A production-ready Model Context Protocol (MCP) server providing Gemini AI capabilities with Google Search grounding and direct model inference.

## 🌟 Features

- **🔍 Google Search Grounding**: Real-time web search using Gemini with Google Search grounding for factual, up-to-date information
- **🤖 Direct Model Inference**: Call Gemini directly for tasks that don't require real-time information
- **📊 JSON Schema Validation**: Strict input/output validation for reliable tool responses
- **🧪 Comprehensive Testing**: Full test suite with schema validation and error handling
- **⚡ High Performance**: Optimized for fast response times

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/gemini-mcp-server.git
   cd gemini-mcp-server
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Set up environment variables:**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your Gemini API key
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Test the server:**
   ```bash
   uv run python test_server.py
   ```

### Getting a Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and add it to your `.env` file

## 🛠️ Available Tools

### 1. `gemini_websearch`
Search the web using Gemini with Google Search grounding.

**Features:**
- ✅ **Real-time search results** with Google Search grounding
- 🌍 **Language support** - Automatically translates results to requested language
- 📊 **Structured output** with proper source attribution
- 🎯 **Custom fields** - Request additional metadata per result

**Parameters:**
- `query` (required): Search query string
- `language` (optional): Language code for result translation (e.g., "es", "fr", "ja")
- `extraFieldsProperties` (optional): Additional fields to include in results

**Example:**
```json
{
  "query": "latest AI developments 2024",
  "language": "es"
}
```

### 2. `gemini_call`
Call Gemini model directly without grounding for structured responses.

**Features:**
- 🎯 **JSON Schema constraints** - Get structured responses that match your schema
- 📝 **Flexible input** - Pass arbitrary data and context
- 🚀 **Fast responses** - Direct model inference without web search
- 💪 **Complex schemas** - Support for nested objects and arrays

**Parameters:**
- `prompt` (required): Instruction describing the task
- `args` (optional): Structured data to include in the prompt
- `outputSchema` (required): JSON Schema defining expected response structure

**Example:**
```json
{
  "prompt": "Analyze this financial data and extract key metrics",
  "args": {
    "revenue": "$1.2B",
    "quarter": "Q3 2024"
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "revenue_usd": {"type": "number"},
      "growth_rate": {"type": "number"}
    }
  }
}
```

## 🔧 Usage with MCP Clients

### Claude Desktop Configuration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "gemini": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/yourusername/gemini-mcp-server",
        "gemini-server"
      ],
      "env": {
        "GEMINI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Other MCP Clients

The server implements the standard MCP protocol and works with any compatible client:

1. **Tool Discovery**: Clients call `list_tools` to see available tools
2. **Tool Execution**: Clients call `call_tool` with tool name and arguments
3. **Response**: Server returns structured JSON responses with validation

## 🧪 Testing

Run the comprehensive test suite:

```bash
uv run python test_server.py
```

The test suite includes:
- ✅ Schema validation tests
- ✅ Success case testing for both tools
- ✅ Error handling validation
- ✅ Input parameter validation
- ✅ Output structure verification
- ✅ Performance monitoring

**Expected Results:**
- All 10 test cases should pass
- Web search tests will show "AFC remote call" logs (indicating real grounding)
- Response times should be under 10 seconds for search operations

## 📊 Performance

- **Search Operations**: ~3-6 seconds (with Google Search grounding)
- **Direct Model Calls**: ~0.5-1 second
- **Schema Validation**: <1ms per request
- **Memory Usage**: ~50MB base + request processing

## 🏗️ Architecture

```
gemini-mcp-server/
├── gemini_mcp_server/          # Main package
│   ├── handlers.py            # Tool implementations
│   ├── server.py              # MCP server core
│   ├── tools.json             # Tool schemas
│   └── __main__.py            # Entry point
├── test_server.py             # Test framework
├── test_cases.json            # Test definitions
└── pyproject.toml             # Dependencies
```

## 🔍 Key Technologies

- **[Google Gemini API](https://ai.google.dev/gemini-api)**: Latest Gemini 2.0 Flash model
- **[Google Search Grounding](https://ai.google.dev/gemini-api/docs/grounding)**: Real-time web search integration
- **[MCP Protocol](https://github.com/modelcontextprotocol)**: Standard for AI tool integration
- **[UV Package Manager](https://github.com/astral-sh/uv)**: Fast Python dependency management

## 🚦 Error Handling

The server includes comprehensive error handling:

- **Invalid API Key**: Clear error messages for authentication issues
- **Network Errors**: Graceful handling of API timeouts and connectivity
- **Schema Validation**: Detailed error messages for malformed requests
- **Rate Limiting**: Automatic retry logic for API rate limits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🔗 Resources

- [Gemini API Documentation](https://ai.google.dev/gemini-api)
- [MCP Protocol Specification](https://github.com/modelcontextprotocol)
- [Google AI Studio](https://aistudio.google.com/)
- [JSON Schema Documentation](https://json-schema.org/)

## 🆘 Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not configured"**
   - Ensure your `.env` file exists and contains a valid API key
   - Check that the key has proper permissions

2. **Tests failing with network errors**
   - Verify internet connectivity
   - Check if API key has rate limiting issues

3. **Schema validation errors**
   - Ensure your requests match the expected input schemas
   - Check the `tools.json` file for parameter requirements

### Getting Help

- Check the test output for detailed error messages
- Review the [Gemini API documentation](https://ai.google.dev/gemini-api)
- Open an issue on GitHub with error logs

---

*Ready to integrate powerful AI capabilities into your applications with real-time web search and structured model inference!* 🚀