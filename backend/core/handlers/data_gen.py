import os
import random
import shutil
import pandas as pd
import numpy as np
from random import shuffle
from utils.common_utils import CommonUtils
from utils.logger_utility import logger


class DataGen(object):
    def __init__(self, seed: int = 1729):
        self.seed = seed

    def sample_means_and_stds(self, value_range, num_means):
        """
        Sample means and standard deviations from a specified range.

        Parameters:
        - seed (int): Random seed for reproducibility.
        - value_range (tuple): Range of values (min, max) for means.
        - num_means (int): Number of means to sample.

        Returns:
        - means (ndarray): Sampled means.
        - std_devs (ndarray): Sampled standard deviations based on means.
        """
        np.random.seed(self.seed)

        means = []
        std_devs = []

        while len(means) < num_means:
            mean = np.random.uniform(value_range[0], value_range[1])
            std_dev = np.random.uniform(0.3, 0.6 * abs(mean))

            if all(abs(mean - m) >= 3 * std_dev for m in means):
                means.append(mean)
                std_devs.append(std_dev)

        return means, std_devs

    def generate_multi_modal_normal(self, value_range, num_modes, mean, std_dev, num_samples=7000):
        """
        Generate a multi-modal normal distribution.

        Parameters:
        - seed (int): Random seed for reproducibility.
        - value_range (tuple): Range of values (min, max).
        - num_modes (int): Number of modes in the distribution.
        - means (list): List of means for each mode.
        - std_devs (list): List of standard deviations for each mode.
        - num_samples (int): Number of samples to generate.

        Returns:
        - samples (ndarray): Generated samples from the multi-modal normal distribution.
        """
        np.random.seed(self.seed)
        samples = np.random.normal(loc=mean, scale=std_dev, size=num_samples)
        # Clip samples to the specified range
        # samples = np.clip(samples, value_range[0], value_range[1])
        return samples

    @staticmethod
    def distribute_sample_across_categories(num_samples, categories):
        category_samples = dict()
        num_categories = len(categories)
        divisor = num_samples % num_categories
        new_num_samples = num_samples - divisor
        # print(new_num_samples)
        quotient = int(new_num_samples / num_categories)
        # print(quotient)
        shuffle(categories)
        # print(categories)
        for c in categories:
            category_samples[c] = quotient
            if divisor == 0:
                continue
            category_samples[c] += 1
            divisor -= 1
        return category_samples

    def simulate_luminescence_vibgyor(self, num_samples=1000):
        colors = ['Violet', 'Indigo', 'Blue', 'Green', 'Yellow', 'Orange', 'Red']
        value_range = (-750, 750)  # Define a range for luminescence values
        num_means = len(colors)

        # Sample means and standard deviations
        means, std_devs = self.sample_means_and_stds(value_range, num_means)
        # logger.debug(means, std_devs)

        # Distribute samples across categories
        category_samples = self.distribute_sample_across_categories(num_samples, colors)
        # print(category_samples)

        # Generate multi-modal normal distribution for luminescence values
        luminescence_data = {}
        for i, color in enumerate(colors):
            # print(f"==={color}")
            # print(category_samples[color])
            luminescence_data[color] = self.generate_multi_modal_normal(value_range, num_means, means[i],
                                                                        std_devs[i],
                                                                        category_samples[color])
            # print(len(luminescence_data[color]))

        return luminescence_data, means, std_devs

    def simulate_xray(self, num_samples=1000):
        colors = ['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7']
        value_range = (-100, 100)  # Define a range for luminescence values
        num_means = len(colors)

        # Sample means and standard deviations
        means, std_devs = self.sample_means_and_stds(value_range, num_means)
        # print(means, std_devs)

        # Distribute samples across categories
        category_samples = self.distribute_sample_across_categories(num_samples, colors)

        # Generate multi-modal normal distribution for luminescence values
        xray_data = {}
        for i, color in enumerate(colors):
            xray_data[color] = self.generate_multi_modal_normal(value_range, num_means, means[i], std_devs[i],
                                                                category_samples[color])

        return xray_data, means, std_devs

    def simulate_gamma(self, num_samples=1000):
        colors = ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7']
        value_range = (-10, 10)  # Define a range for luminescence values
        num_means = len(colors)

        # Sample means and standard deviations
        means, std_devs = self.sample_means_and_stds(value_range, num_means)
        # print(means, std_devs)

        # Distribute samples across categories
        category_samples = self.distribute_sample_across_categories(num_samples, colors)

        # Generate multi-modal normal distribution for luminescence values
        gamma_data = {}
        for i, color in enumerate(colors):
            gamma_data[color] = self.generate_multi_modal_normal(value_range, num_means, means[i], std_devs[i],
                                                                 category_samples[color])

        return gamma_data, means, std_devs

    def assign_random_coordinates(self, df, distance_constraint=5.0, max_retries=10000):
        rng = np.random.default_rng(self.seed)
        coords = [(0.0, 0.0, 0.0)]  # Start with Earth
        coord_set = set(coords)

        n = len(df)
        retries = 0
        limit = distance_constraint / np.sqrt(3)

        while len(coords) <= n and retries < max_retries:
            retries += 1

            # Pick a random existing coordinate
            origin = coords[rng.integers(0, len(coords))]

            # Sample x, y, z offset within constraint cube
            dx = round(rng.uniform(-limit, limit), 3)
            dy = round(rng.uniform(-limit, limit), 3)
            dz = round(rng.uniform(-limit, limit), 3)

            new_coord = (
                round(origin[0] + dx, 3),
                round(origin[1] + dy, 3),
                round(origin[2] + dz, 3)
            )

            if new_coord in coord_set:
                continue  # Duplicate

            # This coordinate is guaranteed to be within distance_constraint
            coords.append(new_coord)
            coord_set.add(new_coord)

        if len(coords) < n:
            raise RuntimeError("Could not generate enough valid coordinates. Try increasing distance_constraint.")

        # Assign to DataFrame
        df['x'] = [c[0] for c in coords[1:]]  # Skip Earth (already handled)
        df['y'] = [c[1] for c in coords[1:]]
        df['z'] = [c[2] for c in coords[1:]]

        return df

    @staticmethod
    def generate_planet_sample(rng) -> dict:
        ether = np.clip(rng.beta(1, 20), 0.001, 0.05)

        rock_noise = (1 - ether * 20) * 0.1
        rock = np.clip(rng.normal(loc=0.3, scale=rock_noise), 0.1, 0.6)

        ideal_water = -4 * (rock - 0.4) ** 2 + 0.5
        water_noise = (1 - ether * 15) * 0.05
        water = np.clip(ideal_water + rng.normal(0, water_noise), 0.05, 0.5)

        air = 0.5 * (rock * water) + 0.2 * (ether ** 0.5)
        air += rng.normal(0, 0.02 * (1 - ether * 10))
        air = np.clip(air, 0.05, 0.4)

        total_no_fire = rock + water + air
        fire = max(0.0, 1.0 - total_no_fire - ether)

        elements = np.array([rock, water, air, fire, ether])
        non_ether_total = elements[:4].sum()
        elements[:4] = elements[:4] / non_ether_total * (1.0 - ether)
        rock, water, air, fire = elements[:4]

        # Liveability score
        liveability = (
                0.35 * np.exp(-((rock - 0.3) ** 2) / 0.02) +
                0.3 * np.exp(-((water - 0.4) ** 2) / 0.02) +
                0.2 * air -
                0.5 * fire ** 2 +
                0.1 * np.sqrt(ether)
        )
        liveability = np.clip(liveability, 0, 1)

        is_liveable = "Yes" if liveability > 0.65 else "No"

        return {
            "Rock": round(rock, 3),
            "Water": round(water, 3),
            "Air": round(air, 3),
            "Fire": round(fire, 3),
            "Ether": round(ether, 4),
            "Liveability": round(liveability, 3),
            "Liveable": is_liveable
        }

    def generate_solar_system_with_ether(self, num_planets: int) -> pd.DataFrame:
        rng = np.random.default_rng(self.seed)

        required_liveable = max(1, int(num_planets * 0.05))

        liveable_list = []
        non_liveable_list = []

        liveable_attempts = 3000
        general_attempts = num_planets * 2

        # 1. Ensure minimum liveable planets
        while len(liveable_list) < required_liveable and liveable_attempts > 0:
            planet = self.generate_planet_sample(rng)
            if planet["Liveable"] == "Yes":
                liveable_list.append(planet)
            liveable_attempts -= 1

        # 2. Fill the rest of the dataset
        while len(liveable_list) + len(non_liveable_list) < num_planets and general_attempts > 0:
            planet = self.generate_planet_sample(rng)
            if planet["Liveable"] == "Yes":
                if len(liveable_list) < required_liveable:
                    liveable_list.append(planet)
                else:
                    non_liveable_list.append(planet)
            else:
                non_liveable_list.append(planet)
            general_attempts -= 1

        all_planets = liveable_list + non_liveable_list
        shuffle(all_planets)

        for i, planet in enumerate(all_planets):
            planet["Planet"] = f"Planet_{i + 1}"

        return pd.DataFrame(all_planets)


class PrepareCodingTask(DataGen):
    def __init__(self, ref_path, path, seed: int = 1729):
        super().__init__(seed)
        self.ref_path = ref_path
        self.path = path

        self._cu_ = CommonUtils()

    def coding_task_1(self, **kwargs):
        # Copy coding task 1
        folder_name = f"coding-task-1"
        dst_path = os.path.join(self.path, folder_name)
        self._cu_.make_dirs(dst_path)
        shutil.copy(src=os.path.join(self.ref_path, folder_name, f"{folder_name}.ipynb"),
                    dst=os.path.join(dst_path, f"{folder_name}.ipynb"))
        self._cu_.zip_files(dst_path,
                            os.path.join(self.path, f"{folder_name}.zip"))
        return True

    def coding_task_2(self, **kwargs):
        try:
            folder_name = f"coding-task-2"
            num_samples = kwargs.get("num_samples", 10000)
            dst_path = os.path.join(self.path, folder_name)
            self._cu_.make_dirs(dst_path)
            shutil.copy(src=os.path.join(self.ref_path, folder_name, f"{folder_name}.ipynb"),
                        dst=os.path.join(dst_path, f"{folder_name}.ipynb"))
            this_path = os.path.join(self.path, folder_name, f"{folder_name}.csv")

            luminescence_values, means, std_devs = self.simulate_luminescence_vibgyor(num_samples)
            luminescence_data = list()

            for k, v in luminescence_values.items():
                luminescence_data.extend(v)

            xray_values, means, std_devs = self.simulate_xray(num_samples)
            xray_data = list()

            for k, v in xray_values.items():
                xray_data.extend(v)

            gamma_values, means, std_devs = self.simulate_gamma(num_samples)
            gamma_data = list()

            for k, v in gamma_values.items():
                gamma_data.extend(v)

            full_data = pd.DataFrame(columns=["lum_data", "xray_data", "gamma_data"])
            full_data["lum_data"] = luminescence_data
            full_data["xray_data"] = xray_data
            full_data["gamma_data"] = gamma_data
            full_data.to_csv(this_path, index=False)
            self._cu_.zip_files(dst_path,
                                os.path.join(self.path, f"{folder_name}.zip"))
            return True
        except Exception as e:
            return False

    def coding_task_3(self, **kwargs):
        folder_name = f"coding-task-3"
        num_samples = kwargs.get("num_samples", 10000)
        dst_path = os.path.join(self.path, folder_name)
        self._cu_.make_dirs(dst_path)
        this_path = os.path.join(self.path, folder_name, f"{folder_name}.csv")
        shutil.copy(src=os.path.join(self.ref_path, folder_name, f"{folder_name}.ipynb"),
                    dst=os.path.join(dst_path, f"{folder_name}.ipynb"))
        df = self.generate_solar_system_with_ether(num_planets=num_samples)
        df.to_csv(this_path, index=False)
        self._cu_.zip_files(dst_path,
                            os.path.join(self.path, f"{folder_name}.zip"))
        return True

    def coding_task_4(self, **kwargs):
        folder_name = f"coding-task-4"
        num_samples = kwargs.get("num_samples", 10000)
        dst_path = os.path.join(self.path, folder_name)
        self._cu_.make_dirs(dst_path)
        shutil.copy(src=os.path.join(self.ref_path, folder_name, f"{folder_name}.ipynb"),
                    dst=os.path.join(dst_path, f"{folder_name}.ipynb"))

        distance_constraint = kwargs.get("distance_constraint", 10.0)
        this_path = os.path.join(self.path, folder_name, f"{folder_name}.csv")
        df = self.generate_solar_system_with_ether(num_planets=num_samples)
        df = self.assign_random_coordinates(df=df, distance_constraint=distance_constraint)
        liveable_planets = df[df["Liveable"] == "Yes"][["Planet", "Liveable"]]
        this_list = list(range(0, len(list(liveable_planets["Liveable"]))))
        this_index = random.choice(this_list)
        target_planet = list(liveable_planets["Planet"])[this_index]
        df.to_csv(this_path, index=False)
        self._cu_.zip_files(dst_path,
                            os.path.join(self.path, f"{folder_name}.zip"))
        return target_planet
