def singleton(cls):
    """
    Make a class a singleton.
    Ensures that only one instance of the class exists.

    Arguments:
        cls: The class to be made a singleton.

    Returns:
        A function that returns the singleton instance of the class.

    Example:
    ```
        @singleton
        class MyClass:
            def __init__(self):
                # Initialization code
                pass
                
        obj1 = MyClass()
        obj2 = MyClass()
        
        obj1 is obj2  # True
    ```
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
