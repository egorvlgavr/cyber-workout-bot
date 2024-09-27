import json
import logging
import os
import random
from abc import ABC
from typing import List, Optional

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


class WorkoutDao(ABC):
    def get_base_exercise(self, train_type: str) -> Optional[dict]:
        pass

    def get_isolated_exercises(self, train_type: str, num_of_workouts: int) -> List[dict]:
        pass


class FileWorkoutDao(WorkoutDao):
    def __init__(self, folder_path: str) -> None:
        self.workouts = []
        for file_name in ['legs_workouts.json', 'back_workouts.json',
                          'shoulders_workouts.json', 'top_workouts.json']:
            file_path = folder_path + "/" + file_name
            with open(file_path, 'r') as workoutsFile:
                from_file = json.load(fp=workoutsFile)
                logger.info("[%d] workouts was loaded from file [%s]",
                            len(from_file), file_path)
                self.workouts.extend(from_file)
        logger.info("Total workouts: [%d]", len(self.workouts))

    def get_base_exercise(self, train_type: str) -> Optional[dict]:
        base_workouts = list(
            filter(lambda elem: elem['type'] == 'base' and elem['group'] == train_type, self.workouts)
        )
        if len(base_workouts) > 0:
            return random.choice(base_workouts)
        else:
            return None

    def get_isolated_exercises(self, train_type: str, num_of_workouts: int) -> List[dict]:
        isolated_workouts = list(
            filter(lambda elem: elem['type'] == 'isolated' and elem['group'] == train_type, self.workouts)
        )
        if len(isolated_workouts) > num_of_workouts:
            return random.sample(isolated_workouts, num_of_workouts)
        else:
            return isolated_workouts


TOTAL_BASE_WORKOUTS = 1
TOTAL_ADDITIONAL_WORKOUTS = 1
workout_dao = FileWorkoutDao(os.environ.get('DATA_PATH', 'data'))


def create_training_plan(requested_workouts: List[str], num_of_workouts: int) -> List[str]:
    training_plan = list()
    if len(requested_workouts) > 0:
        # base workout logic
        base_exercise = workout_dao.get_base_exercise(requested_workouts[0])
        if not base_exercise:
            return list()
        training_plan.append(base_exercise['description'])
        # isolated workout logic
        num_of_additional = TOTAL_ADDITIONAL_WORKOUTS if len(requested_workouts) > 1 else 0
        num_of_isolated = num_of_workouts - TOTAL_BASE_WORKOUTS - num_of_additional
        isolated = workout_dao.get_isolated_exercises(requested_workouts[0], num_of_isolated)
        training_plan.extend(map(lambda elem: elem['description'], isolated))
        # additional workout logic
        if len(requested_workouts) > 1:
            additional = workout_dao.get_isolated_exercises(requested_workouts[1], num_of_additional)
            training_plan.extend(map(lambda elem: elem['description'], additional))
    return training_plan
