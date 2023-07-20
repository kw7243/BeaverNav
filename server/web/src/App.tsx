import { useState } from 'react'
import { getRouteImage, sendRoutingRequest } from './api'

function App() {
  const [origin, setOrigin] = useState<string | undefined>(undefined)
  const [destination, setDestination] = useState<string | undefined>(undefined)
  const [images, setImages] = useState<Array<{ text: string, imageSrc: string }>>([])

  const getDirections = async () => {
    if (origin !== undefined && origin !== '' && destination !== undefined && destination !== '') {
      const response = await sendRoutingRequest(origin, destination)
      if (response) {
        const routeImages = response.map(async (routeResponse) => {
          const imageSrc = await getRouteImage(routeResponse.image_filepath)
          return {
            text: routeResponse.text,
            imageSrc: imageSrc!,
          }
        })

        setImages(await Promise.all(routeImages))
      }
    }
  }

  return (
    <div className='w-screen h-screen flex flex-col justify-center items-center space-y-10'>
      <div>
        <label htmlFor="origin" className="block text-sm font-medium text-gray-700">Origin</label>
        <input onChange={e => setOrigin(e.target.value)} type="text" name="origin" id="origin" className="block w-full mb-5 rounded-md border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
        <label htmlFor="destination" className="block text-sm font-medium text-gray-700">Destination</label>
        <input onChange={e => setDestination(e.target.value)} type="text" name="destination" id="destination" className="block w-full mb-5 rounded-md border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
        <button onClick={getDirections} className="mx-2 my-2 bg-indigo-700 transition duration-150 ease-in-out hover:bg-indigo-600 rounded text-white px-6 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-offset-2  focus:ring-indigo-600">Get Directions</button>
      </div>
      <div className='flex flex-col space-y-5'>
        {images.map(({ text, imageSrc }) => {
          return (
          <div key={imageSrc}>
            <p className='mb-5'>{text}</p>
            <img src={imageSrc} />
          </div>
          )
        })}
      </div>
    </div>
  )
}

export default App
