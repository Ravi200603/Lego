Guide to run the program 

The Program can we run by two types 
1) Non Ui Version: 
   a. Go inside Lego folder and run the main_terminal.py
   b. wait until the its generating the images on the terminal
   c. Once Completed FinalResults.jpg named file will be saved in the files 
   d. Open it and see the preview of final image & error and all could be seen directly at the terminal itself

2) Ui Version
Ui Version requries to run two server 1st for the react page and 2nd for the flask for backend.
    //starting react server 
    a. inside lego folder open terminal and type 
    cd front_end

    b. you will be in front_end folder now and there type 
    npm install

       to install the necessary node modules
    c. thirdly type
    npm run dev

    // starting flask server
    a. go to new terminal and type 
    cd Lego

    b. once you are in Lego folder type 
    python server.py 

    now you both the servers are ready and now you can go to this address 
    http://localhost:5174/
    Note: Port number might be different here please check it from the front_end termainl 

    After oping this image you can add image from this file itself or your choice and click on upload button

    Once that is done it will send image to python file and python will execute it and once its done and image is ready, image will pop up on the website ui itself 
    Note: It might take few minutes to generate image as making 10k Generations taking longer in python server
