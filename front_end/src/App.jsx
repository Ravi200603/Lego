import React, { useState } from 'react'
import './App.css'

function App() {
    /**const states**/
  const [selectedFile, setSelectedFile] = useState(null);
  const [resultImage, setResultImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  /*funct to handle selecting the file */
  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  /*hnadle posting the original image and any errors that may come up */
  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Please select a file first!");
      return;
    }

    const formData = new FormData();
    formData.append('image', selectedFile);

    setIsLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/lego', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
          console.error("Upload failed");
      } else {
          const blob = await response.blob();
          setResultImage(URL.createObjectURL(blob));
      }
    } catch (error) {
      console.error("Error connecting to Flask:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
    <nav className='shadow-md'>
      <h1 className='font-bold text-2xl text-center m-2 p-2 bg-[#fafafc]'>Lego Mosaic</h1>
    </nav>
    <div>
      <h1 className='font-semibold text-4xl mt-6 text-center'>Turn your pet into brick masterpiece.</h1>
      <p className='text-center'>
        Upload a picture of your buddy and watch it turning into the brick art masterpiece
      </p>
      <div className='bg-white shadow-md mx-auto w-[50%] h-72 rounded-2xl m-5 p-2 flex flex-col '>
      <img className='w-20 h-20 mx-auto m-3' src="../icons/uploadIcon.png" alt="Upload Icon"/>
      <p className='text-center font-semibold text-2xl'> Drop your buddy here</p>
      <span className=' block text-center'>PNG or JPG files accepted only</span>
      
      <input className="block mx-auto w-[25%] bg-gray-100 rounded rounded-lg " type="file" accept=".png,.jpg,.jpeg" onChange={handleFileChange}/>
    
      <button onClick={handleUpload} className="bg-[#386ce8] text-white font-extrabold p-2 rounded-lg block w-fit mx-auto mt-2 cursor-pointer">
          Upload Your Pic Here
      </button>
      {resultImage && (
          <div className="text-center mt-5">
            <h2 className="text-xl font-bold">Result:</h2>
            <img src={resultImage} alt="Result" className="mx-auto mt-3" />
          </div>
        )}
    </div>
    </div>

    </div>
  )
}

export default App