# Set TOKENIZERS_PARALLELISM environment variable
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Required Libraries
import requests
from bs4 import BeautifulSoup
from bertopic import BERTopic
from bertopic.plotting import visualize_topics
import pandas as pd
import plotly.express as px

from umap import UMAP
from hdbscan import HDBSCAN

umap_model = UMAP(n_neighbors=15, min_dist=0.0, n_components=2, metric="cosine")
hdbscan_model = HDBSCAN(
    min_cluster_size=2, min_samples=1, cluster_selection_epsilon=0.5
)


# Function to Scrape a Website
def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    content = [
        paragraph.get_text(strip=True)
        for paragraph in soup.find_all("p")
        if len(paragraph.get_text(strip=True)) > 0
        and isinstance(paragraph.get_text(strip=True), str)
    ]
    return content


# Custom Visualization Function
def custom_visualize_topics(topic_model, topics, documents, n_neighbors=10, **kwargs):
    topic_model.umap_model.n_neighbors = n_neighbors
    embeddings = topic_model._extract_embeddings(documents)
    umap_embeddings = UMAP(
        n_neighbors=n_neighbors, n_components=2, metric="cosine", random_state=42
    ).fit_transform(embeddings)

    viz_df = pd.DataFrame(umap_embeddings, columns=["x", "y"])
    viz_df["Topic"] = topics
    viz_df["Document"] = documents  # Add documents to the DataFrame

    # Truncate the hover text to the specified maximum length
    max_hover_text_length = 250
    viz_df["TruncatedDocument"] = viz_df["Document"].apply(
        lambda x: x[:max_hover_text_length] + "..."
        if len(x) > max_hover_text_length
        else x
    )

    fig = px.scatter(
        viz_df,
        x="x",
        y="y",
        color="Topic",
        hover_name="TruncatedDocument",  # Use truncated document instead of original document
        color_continuous_scale="viridis",
    )

    fig.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
            "margin": {
                "r": 0,
                "t": 0,
                "l": 0,
                "b": 0,
                "pad": 0,
            },
        }
    )

    fig.show()


def get_topic_coordinates(model):
    topic_freq = model.get_topic_freq()  # Get the topic frequencies
    topics = topic_freq["Topic"].values.tolist()
    probabilities = (topic_freq["Count"] / topic_freq["Count"].sum()).tolist()

    topic_coordinates = {"Topic": topics, "Probability": probabilities}

    return pd.DataFrame(topic_coordinates)


def main():
    url = "https://en.wikipedia.org/wiki/World_War_II"  # Replace with the URL you want to scrape
    print(f"Scraping {url}...")
    scraped_content = scrape_website(url)

    if len(scraped_content) < 2:
        print("Not enough content for topic modeling.")
        return

    # Create BERTopic Model
    umap_model = UMAP(n_neighbors=5, min_dist=0.3, n_components=2, metric="cosine")
    model = BERTopic(language="english", umap_model=umap_model, min_topic_size=10)
    topics, _ = model.fit_transform(scraped_content)

    # Show the topics and their most frequent words
    topic_words = model.get_topic_freq()
    print(topic_words)

    # Print the top N tokens for each identified topic
    N = 25  # Change N to display more or fewer tokens for each topic
    topic_representation = model.get_topic_info()  # Get the top N tokens for each topic
    print("\nTop Tokens for Each Topic:")
    for index, row in topic_representation.head(N).iterrows():
        print(f"Topic {row['Topic']}: {row['Name']}")

    # Visualize topics and their frequency
    if len(topic_words) > 1:
        custom_visualize_topics(model, topics, scraped_content, n_neighbors=10)
    else:
        print("Not enough topics to visualize")

    # Print topics assigned to each scraped paragraph
    print("\nAssigned Topics for Scraped Content:")
    for index, document in enumerate(scraped_content):
        print(f"Document {index + 1} (Topic {topics[index]}): {document}")

    # Transform new documents
    new_document = ["This is a new document"]
    new_topic, new_probability = model.transform(new_document)
    print("\nNew Document Topic:")
    print(new_topic)


if __name__ == "__main__":
    main()
