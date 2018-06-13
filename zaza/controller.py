import logging
from juju.controller import Controller
from zaza import sync_wrapper


async def async_add_model(model_name, config=None):
    """Add a model to the current controller

    :param model_name: Name to give the new model.
    :type model_name: str
    :param config: Model configuration.
    :type config: dict"""
    controller = Controller()
    await controller.connect()
    logging.debug("Adding model {}".format(model_name))
    model = await controller.add_model(model_name, config=config)
    await model.connect()
    model_name = model.info.name
    await model.disconnect()
    await controller.disconnect()
    return model_name

add_model = sync_wrapper(async_add_model)


async def async_destroy_model(model_name):
    """Remove a model from the current controller

    :param model_name: Name of model to remove
    :type model_name: str"""
    controller = Controller()
    await controller.connect()
    logging.debug("Destroying model {}".format(model_name))
    await controller.destroy_model(model_name)
    await controller.disconnect()

destroy_model = sync_wrapper(async_destroy_model)


async def async_get_cloud():
    """Return the name of the current cloud

    :returns: Name of cloud
    :rtype: str
    """
    controller = Controller()
    await controller.connect()
    cloud = await controller.get_cloud()
    await controller.disconnect()
    return cloud

get_cloud = sync_wrapper(async_get_cloud)


async def async_list_models():
    """Return a list of tha available clouds

    :returns: List of clouds
    :rtype: list
    """
    controller = Controller()
    await controller.connect()
    models = await controller.list_models()
    await controller.disconnect()
    return models

list_models = sync_wrapper(async_list_models)
