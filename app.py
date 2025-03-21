from flask import Flask, request, jsonify
import psycopg2
from kubernetes import client, config
import logging

app = Flask(__name__)

# Database connection details
DB_HOST = "postgres-db"  # k8s service name this should be same as in postgres-service.yaml file that we have created
DB_NAME = "nrp_db"
DB_USER = "admin"
DB_PASSWORD = "password"

# Set up logging to show logs 
logging.basicConfig(level=logging.DEBUG)
#function to connect to the database based on credentials 
def get_db_connection():
    try:
        app.logger.debug("Connecting to PostgreSQL database at postgres-db")
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        app.logger.debug("Successfully connected to PostgreSQL database")
        return conn
    except Exception as e:
        app.logger.error(f"Failed to connect to PostgreSQL database: {e}")
        raise
#this is used to get all the pods present in our namespace nrp this is an api call to k8s python api that gives us our list of pods this is not any call going to our local database 
@app.route('/pods', methods=['GET'])
def get_pods():
    try:
        app.logger.debug("Fetching running pods")
        config.load_incluster_config() 
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace="nrp")
        pod_names = [pod.metadata.name for pod in pods.items]
        app.logger.debug(f"Running pods: {pod_names}")
        return jsonify(pod_names)
    except Exception as e:
        app.logger.error(f"Error fetching pods: {e}")
        return jsonify({"error": str(e)}), 500
#this route is used to store pods in database in our local database we can store pods in our database..no matter if it is running or not this is just a use case to show hot to store pods in our database...this means that if i insert a pod that is not running in my namespace then it will not show in get_pods route 
@app.route('/store-pods', methods=['POST'])
def store_pods():
    try:
        app.logger.debug("Received request to store pods")
        pod_names = request.json.get('pod_names')
        if not pod_names:
            return jsonify({"error": "No pod names provided"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        for pod_name in pod_names:
            app.logger.debug(f"Storing pod: {pod_name}")
            cur.execute("INSERT INTO pods (name) VALUES (%s)", (pod_name,))

        conn.commit()
        cur.close()
        conn.close()

        app.logger.debug("Pod names stored successfully")
        return jsonify({"message": "Pod names stored successfully"}), 201
    except Exception as e:
        app.logger.error(f"Error storing pods: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
