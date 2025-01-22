from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

SERP_API_KEY = "435972e90f46963135e2ebabc9fc605b1e63e2308ba22325b203c740f812f982"  # Replace with your actual SerpApi key

@app.route('/api/competitor-analysis', methods=['POST'])
def competitor_analysis():
    try:
        # Get the input URL from the user
        url = request.json.get("url")
        if not url:
            return jsonify({"error": "URL is required"}), 400

        # Extract the domain
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]

        # Step 1: Identify the Competitor's Primary Keyword
        query = {"q": f"site:{domain}", "api_key": SERP_API_KEY}
        response = requests.get("https://serpapi.com/search.json", params=query)
        data = response.json()

        primary_keyword = data.get("organic_results", [{}])[0].get("title", "N/A")

        # Step 2: Analyze Search Performance
        search_query = {"q": primary_keyword, "api_key": SERP_API_KEY}
        search_response = requests.get("https://serpapi.com/search.json", params=search_query)
        search_data = search_response.json()

        top_ranked_websites = [
            {"title": result.get("title", "N/A"), "link": result.get("link", "N/A")}
            for result in search_data.get("organic_results", [])[:5]
        ]

        # Mocked Data for Steps 3-5
        content_audit = {
            "top_blogs": ["Blog A", "Blog B", "Blog C"],
            "organic_traffic": "15,000 visitors/month",
            "backlink_profiles": "250 backlinks",
        }

        traffic_metrics = {
            "organic_traffic": "20,000 visitors/month",
            "overall_traffic": "50,000 visitors/month",
        }

        cta_analysis = {
            "common_ctas": ["Sign up now", "Learn more", "Download the guide"],
            "cta_placements": ["Homepage banner", "End of blog posts", "Pop-ups"],
        }

        # Combine all data into the final output
        result = {
            "primary_keyword": primary_keyword,
            "top_ranked_websites": top_ranked_websites,
            "content_audit": content_audit,
            "traffic_metrics": traffic_metrics,
            "cta_analysis": cta_analysis,
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
