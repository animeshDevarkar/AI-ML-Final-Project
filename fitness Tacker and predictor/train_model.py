def calculate_calories(activity, weight, duration):
    activity_factors = {
        'running': 9.8,
        'cycling': 7.5,
        'swimming': 8.3
    }
    factor = activity_factors.get(activity, 0)
    calories = factor * weight * duration
    return round(calories, 2)
