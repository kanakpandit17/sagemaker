import streamlit as st
import boto3
from datetime import datetime, time, date
from os import getenv
from dotenv import load_dotenv
load_dotenv()

dynamodb = boto3.resource('dynamodb', region_name='us-east-1', aws_access_key_id=getenv('aws_access_key_id'), aws_secret_access_key=getenv('aws_secret_access_key'))
table = dynamodb.Table(getenv('dynamodbb'))

def main():
    st.title("Task Management System")
    task = st.text_input("Enter a new task:")
    deadline_time = st.time_input("Add a deadline (Time):")
    deadline = time(hour=deadline_time.hour, minute=deadline_time.minute)
    
    if st.button("Add Task"):
        deadline_str = deadline.strftime("%H:%M:%S")
        table.put_item(Item={'task': task, 'deadline': deadline_str, 'completed': False})
        st.success("Task added successfully!")
    
    tasks = table.scan()['Items']
    
    if tasks:
        st.subheader("Tasks:")
        for i, task in enumerate(tasks):
            task_text = task['task']
            completed = task.get('completed', False)
            deadline_str = task.get('deadline', '')
            deadline_dt = datetime.strptime(deadline_str, "%H:%M:%S").time() if deadline_str else None
            st.write(f"{i + 1}. {task_text}")
            st.write(f"Deadline: {deadline_dt}" if deadline_dt else "No deadline")
            
            if not completed:
                if st.button(f"Mark as Completed {i + 1}"):
                    table.update_item(
                        Key={'task': task_text},
                        UpdateExpression='SET completed = :val',
                        ExpressionAttributeValues={':val': True}
                    )
                    st.success("Task marked as completed!")
            else:
                st.write("Status: Completed")
            
            if st.button(f"Edit Task {i + 1}"):
                updated_task = st.text_input("Update the task:", value=task_text)
                updated_deadline_time = st.time_input("Update the deadline (Time):", value=deadline_dt) if deadline_dt else None
                
                if updated_deadline_time:
                    updated_deadline = time(hour=updated_deadline_time.hour, minute=updated_deadline_time.minute)
                    updated_deadline_str = updated_deadline.strftime("%H:%M:%S")
                else:
                    updated_deadline_str = None
                
                table.update_item(
                    Key={'task': task_text},
                    UpdateExpression='SET task = :task, deadline = :deadline',
                    ExpressionAttributeValues={':task': updated_task, ':deadline': updated_deadline_str}
                )
                st.success("Task updated successfully!")
            
            if st.button(f"Delete Task {i + 1}"):
                table.delete_item(Key={'task': task_text})
                st.success("Task deleted successfully!")
        st.write("---")


if __name__ == '__main__':
    main()