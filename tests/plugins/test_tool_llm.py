from unittest.mock import patch, AsyncMock
import pytest
from plugins.tool_llm import LLMTool
from core.context import SharedContext
import logging
import os
import yaml
import asyncio


@pytest.fixture
def temp_config_file(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "settings.yaml"
    config_data = {"llm": {"model": "test-model"}}
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield
    os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_llm_tool_execute_with_config(temp_config_file):
    llm_tool = LLMTool()
    llm_tool.setup({})

    # Simulate the kernel's behavior: user input is in context, and also in history.
    context = SharedContext(
        session_id="test",
        current_state="THINKING",
        user_input="Hello",
        history=[{"role": "user", "content": "Hello"}],
        logger=logging.getLogger("test"),
    )

    assert llm_tool.model == "test-model"

    mock_response = AsyncMock()
    mock_response.choices[0].message.content = "Hi there!"

    with patch(
        "litellm.acompletion", new_callable=AsyncMock, return_value=mock_response
    ) as mock_acompletion:
        result_context = await llm_tool.execute(context)

        # The tool should now be called with the history, which includes the user input.
        mock_acompletion.assert_called_once_with(
            model="test-model",
            messages=[
                {
                    "role": "system",
                    "content": "You are Sophia, an Artificial Mindful Intelligence.",
                },
                {"role": "user", "content": "Hello"},
            ],
            timeout=30.0,
        )
        assert result_context.payload["llm_response"] == "Hi there!"


@pytest.mark.asyncio
async def test_llm_tool_timeout_handling(temp_config_file):
    """Test that LLM tool properly handles timeouts using asyncio.wait_for."""
    llm_tool = LLMTool()
    llm_tool.setup({})

    context = SharedContext(
        session_id="test",
        current_state="THINKING",
        user_input="Test timeout",
        history=[{"role": "user", "content": "Test timeout"}],
        logger=logging.getLogger("test"),
    )

    # Mock litellm.acompletion to hang indefinitely
    async def slow_mock(*args, **kwargs):
        await asyncio.sleep(100)  # Simulate a very slow API call
    
    with patch("litellm.acompletion", new_callable=AsyncMock, side_effect=slow_mock):
        result_context = await llm_tool.execute(context)
        
        # Should return timeout error message
        assert "timeout" in result_context.payload["llm_response"].lower()

