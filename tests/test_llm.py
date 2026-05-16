"""LLM 客户端单元测试"""
import pytest
from unittest.mock import patch, MagicMock
from agent.llm import LLMClient


class TestLLMClient:
    def test_init_defaults(self):
        client = LLMClient(api_key="sk-test")
        assert client.model == "deepseek-chat"
        assert client.base_url == "https://api.deepseek.com"

    @patch("agent.llm.OpenAI")
    def test_chat_returns_content(self, mock_openai):
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "SELECT * FROM students;"
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        client = LLMClient(api_key="sk-test")
        client._client = mock_openai.return_value

        result = client.chat("You are a SQL expert.", "查询所有学生")
        assert result == "SELECT * FROM students;"

    @patch("agent.llm.OpenAI")
    def test_chat_json_appends_json_instruction(self, mock_openai):
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = '{"sql": "SELECT 1"}'
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        client = LLMClient(api_key="sk-test")
        client._client = mock_openai.return_value

        result = client.chat_json("You are helpful.", "Give me JSON")
        assert result == '{"sql": "SELECT 1"}'
