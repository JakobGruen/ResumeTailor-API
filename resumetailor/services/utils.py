from pydantic import BaseModel
import yaml
import json
from rich import print


def str_to_model(data_str: str, model: BaseModel, format: str = "json") -> BaseModel:
    """
    Load a BaseModel object from a JSON or YAML string.
    format: 'json' (default) or 'yaml'
    """
    if format == "yaml":
        data = yaml.safe_load(data_str)
    else:
        data = json.loads(data_str)
    return model(**data)


def model_to_str(model: BaseModel | list[BaseModel], format: str = "json") -> str:
    """
    Convert a BaseModel object or a list of BaseModel objects to a JSON or YAML string.
    format: 'json' (default) or 'yaml'
    """
    if isinstance(model, list):
        data = [m.model_dump() for m in model]
    else:
        data = model.model_dump()
    if format == "yaml":
        return yaml.dump(data, sort_keys=False)
    else:
        return json.dumps(data, indent=2)
