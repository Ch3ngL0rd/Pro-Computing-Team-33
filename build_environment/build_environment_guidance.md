## System version



OS version：Microsoft Windows 10 10.0.19045

Anaconda version: conda 23.3.1

Anaconda is an open source distribution for data science and machine learning. Anaconda provides an integrated environment that makes it easier to install, manage, and switch between different tools and libraries. Please ensure that anaconda is installed on your computer.

## Steps to Build Environment

1. Open anaconda prompt

![image-20230831153150751](C:\Users\LiTao_smartmore\AppData\Roaming\Typora\typora-user-images\image-20230831153150751.png)

2. Switch to the directory where `environment. yml` is located and run the following command

```
conda env create -f environment.yml
```

then you will now create the `sqlite_` environment

![image-20230831153548592](C:\Users\LiTao_smartmore\AppData\Roaming\Typora\typora-user-images\image-20230831153548592.png)

4. Switch to ` sqlite_` environment

```
conda activate sqlite_
```

5. View owned packages for the current environment

```
conda list
```

sqlite3, pandas, openpyxl are all available

![image-20230831154218889](C:\Users\LiTao_smartmore\AppData\Roaming\Typora\typora-user-images\image-20230831154218889.png)