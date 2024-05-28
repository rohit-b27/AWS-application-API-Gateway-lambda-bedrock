import boto3
import botocore.config
import json 
from datetime import datetime

def content_generation_bedrock(question:str)->str:
    prompt = f"""
    <s>[INST]Human: You are an experienced data science professional assistant, answer the questions accordingly {question}
    Assistant:[/INST]</s>"""
    
    body = {
        "prompt": prompt,
        "max_gen_len": 1000,
        "temperature": 0.5,
        "top_p":0.9
        } 
    
    try:
        bedrock = boto3.client("bedrock-runtime",region_name="us-east-1",
                               config = botocore.config.Config(read_timeout=300, retries={'max_attempts':3}))
        response = bedrock.invoke_model(body=json.dumps(body),modelId="meta.llama3-8b-instruct-v1:0")
        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        print(response_data)
        answer = response_data['generation']
        return answer
    
    except Exception as e:
        print(f"Error generating the answer:{e}")
        return "" 
    
def lambda_handler(event, context):
    event = json.loads(event['body'])
    question = event['question']
    generate_answer = content_generation_bedrock(question=question)
    if generate_answer:
        current_time=datetime.now().strftime('%H%M%S')
        s3_key = f"question-answer-output/{current_time}.txt"
        s3_bucket = 'awsbedrockapp1'
        save_answer_details_s3(s3_key,s3_bucket,generate_answer)
    else:
        print("no response generated")
    return {
        'statusCode': 200,
        'body': json.dumps('response generated')
    }

def save_answer_details_s3(s3_key,s3_bucket,generate_answer):
    s3=boto3.client('s3')
    
    try:
        s3.put_object(Bucket = s3_bucket, Key = s3_key, Body = generate_answer)
        print("code saved to s3")
    except Exception as e: 
        print("Error when saving the code to s3")

        
        
        
    
