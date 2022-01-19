from airflow import DAG
from airflow.models.dag import dag
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from random import randint
from airflow.models.xcom import XCom
from  datetime import datetime

def _choosing_best_model(ti):
    accuracies = ti.xcom_pull(task_ids=[
    'train_1',
    'train_2',
    'train_3'])
    print(accuracies)
    return accuracies.index(max(accuracies))

a_dag= DAG("test", 
start_date=datetime(2021, 3 ,11),
schedule_interval='@hourly',
catchup=True)

training_model_tasks = [ 
    BashOperator( dag=a_dag, 
    task_id=f"train_{model_id}",
    bash_command= 'python3 /root/airflow/dags/go.py -d /root/airflow/dags/dataset -m' + " /root/airflow/dags/"+ str(model_id) + '.h5 -l' + " /root/airflow/dags/"+str(model_id) + '.pickle -p' + " /root/airflow/dags/"+ str(model_id) + ".png  -e  1",
# op_kwargs={
# "model_id": model_id,
# "input_shape":(255,255,3),
# }
)
     for model_id in ['1','2','3']
    
]


def smtp(**kwargs):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    from datetime import datetime

    sender_address = '**************'
    sender_pass = '*****'
    receiver_address = '************'
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    f = open("/root/airflow/dags/file.txt", "r")
    message['Subject'] = 'apache airflow ok '+ f.read()
    message.attach(MIMEText(str(datetime.today()), 'plain') )
    session = smtplib.SMTP('smtp.gmail.com', 587) 
    session.starttls() 
    session.login(sender_address, sender_pass) 
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    import os
    os.system('rm -rf /root/airflow/dags/*.txt')

    



load= BashOperator(task_id="load",bash_command='sshpass -p ***** scp  -r *******  /root/airflow/dags')


email_ = PythonOperator(
task_id='send_best',
python_callable=smtp,
dag=a_dag
)





choosing_best_model = PythonOperator(
task_id="choose",
python_callable=_choosing_best_model,
dag=a_dag
)


def arch(**kwargs):
    import os
    ti= kwargs['ti']
    id=ti.xcom_pull(task_ids='choose')
    if id==0:
        id=1
    if id ==1:
        id=2
    if id==2:
        id==3

    ct = datetime.now()
    t = ct.timestamp()
    #"/root/airflow/dags/"+str(id)+".h5 "
    os.system('export GZIP=-9 && tar -cvzf'+ "/root/airflow/dags/"+str(t)+str("test")+".tar.gz " + "/root/airflow/dags/"+str(id)+".pickle "+"/root/airflow/dags/"+str(id)+".png " + "/root/airflow/dags/"+str(id)+".h5 "+"/root/airflow/dags/"+str(id)+"*weights*")
    ti.xcom_push(key="archive",value=t)

def yandex_console(**kwargs):
     ti= kwargs['ti']
     import os
     os.system("yandex-disk start --dir=/root/airflow/dags/models")
     os.system ("yandex-disk publish /root/airflow/dags/*.tar.gz --dir=/root/airflow/dags/models > /root/airflow/dags/file.txt ")
   

make_arch=PythonOperator(task_id="archive",python_callable=arch)

yandex=PythonOperator(task_id="yandex",python_callable=yandex_console)

clear=BashOperator(task_id="clear",bash_command="rm -rf  /root/airflow/dags/*.tar.gz /root/airflow/dags/*.h5  /root/airflow/dags/*.png /root/airflow/dags/*.pickle && yandex-disk stop --dir=/root/airflow/dags/models && rm -vr /root/airflow/dags/models /root/airflow/dags/dataset")



load >> training_model_tasks >> choosing_best_model >> make_arch >> yandex >> [clear,  email_] 
