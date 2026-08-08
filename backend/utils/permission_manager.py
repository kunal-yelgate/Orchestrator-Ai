from config.agent_config import AGENT_CONFIGS


class PermissionManager:

    @staticmethod
    def validate(agent_name: str):
        config = AGENT_CONFIGS.get(agent_name)

        if config is None:
            raise PermissionError(
                f"No configuration found for '{agent_name}'."
            )

        return config

    @staticmethod
    def require_network(agent_name: str):
        config = PermissionManager.validate(agent_name)

        if not config.allow_network:
            raise PermissionError(
                f"{agent_name} is not allowed to access the network."
            )

    @staticmethod
    def require_file_write(agent_name: str):
        config = PermissionManager.validate(agent_name)

        if not config.allow_file_write:
            raise PermissionError(
                f"{agent_name} is not allowed to write files."
            )

    @staticmethod
    def require_tool(agent_name: str, tool: str):
        config = PermissionManager.validate(agent_name)

        if tool not in config.allowed_tools:
            raise PermissionError(
                f"{agent_name} cannot use tool '{tool}'."
            )