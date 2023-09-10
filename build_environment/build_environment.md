### System version

OS version：Microsoft Windows 10 

python version: python 3.11.3

### steps to build environment

1. Enter your project directory and create a virtual environment using the following command

``` 
python -m venv myenv
```



![image-20230902170429313](build_environment.assets/image-20230902170429313.png)



2. If you are on a Windows system, switch to myenv/Scripts, run activate, enter the virtual environment, and then switch back

```
cd myenv/Scripts
activate
cd ..
cd ..
```

![image-20230902170600880](build_environment.assets/image-20230902170600880.png)

If you are on Mac OS or Linux, use the following command to activate the virtual environment

``` 
source myenv/bin/activate
```

3. Install the required package using the following command

```
pip install -r requirements.txt
```



![image-20230902170726076](build_environment.assets/image-20230902170726076.png)



4. Check if the package is available. It can be seen that pandas, sqlite3, and openpyxl are all available, while Skylearn is not installed, so it will display that this module is not available.

![0a5fb60b85da794e567c769d3966ee5f](build_environment.assets/0a5fb60b85da794e567c769d3966ee5f.png)