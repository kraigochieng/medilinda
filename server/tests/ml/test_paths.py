from medilinda_ml.paths import DATA_DIR


def test_the_training_data_folder_holds_the_training_csv() -> None:
    assert (DATA_DIR / "data.csv").is_file()
