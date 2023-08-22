import numpy as np
from pathlib import Path
from src.parameters import Parameters
from src.user_config import UserConfig
from src import draw_routine

repo_root = Path(__file__).parent.parent

config_file = str(repo_root / "configs" / "config_099.json")
user_config = UserConfig.load_from_file(filename=config_file,
                                        output_directory=str(repo_root / "output"))
parameters = Parameters.load_from_file(filename=config_file)
parameters.total_porosity_margin = 3.0
parameters.porosity_foam_pore_margin = 3.0

amount_runs = 10
total_poros = np.zeros(shape=amount_runs)
foam_poros = np.zeros(shape=amount_runs)

for i in range(0, amount_runs):
    actual_porosities = draw_routine.generate_image(user_config, parameters, save=False)
    total_poros[i] = actual_porosities.total
    foam_poros[i] = actual_porosities.by_foam_pores

print("desired poros", str(user_config.desired_porosities))
print("total poro mean", np.mean(total_poros), "var", np.var(total_poros))
print("foam poro mean", np.mean(foam_poros), "var", np.var(total_poros))



