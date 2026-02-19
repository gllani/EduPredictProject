import matplotlib.pyplot as plt

def plot_distribution(series):
    plt.figure()
    plt.hist(series)
    plt.title("Distribution")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.show()