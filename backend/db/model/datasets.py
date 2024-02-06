

class Datasets:
    paths = {
        "a": "a.csv",
        "b": "b.csv",
        "c": "c.csv",
    }

    ticks = {
        "a": 100,
        "b": 100,
        "c": 100,
    }

    def exists(bot_id):
        return bot_id in Datasets.paths

    def validate_string(dataset_string):
        if not Datasets.exists(dataset_string):
            raise Exception("Dataset does not exist")

        return dataset_string

    def ensure_ticks(dataset_string, min_ticks):
        Datasets.validate_string(dataset_string)

        if Datasets.ticks[dataset_string] < min_ticks:
            raise Exception("Dataset does not have enough ticks")

        return dataset_string
