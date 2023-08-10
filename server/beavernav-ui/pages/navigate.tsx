import Link from "next/link";
import Image from "next/image";
import logoImg from '../public/FindYourWay.png'
import { useState, useEffect } from "react";
import { sendRoutingRequest, RouteResponse } from "../utilities/api";
import { showNotification } from "@mantine/notifications";
import { XCircleIcon } from "@heroicons/react/24/outline";
import "react-responsive-carousel/lib/styles/carousel.min.css";
import { Carousel } from "react-responsive-carousel";


const MULTIPLE_FLOORS_API = "http://127.0.0.1:5000/interfloorplan";
const SINGLE_FLOOR_API = "http://127.0.0.1:5000/intrafloorplan";

const navigation = [
    { name: 'Navigate', href: '/navigate' },
]

export default function Navigate() {
    const [origin, setOrigin] = useState('')
    const [destination, setDestination] = useState('')
    const [images, setImages] = useState<RouteResponse[]>([])

    const fetchImages = async () => {
        const imageURIs = await sendRoutingRequest(origin, destination)
        if (imageURIs === undefined) {
            showNotification({
                title: 'Network Error',
                message: 'An error occurred when getting the route.',
                autoClose: 3000,
                color: 'red',
                icon: <XCircleIcon />,
            })
        } else {
            setImages(imageURIs)
        }
    }

    useEffect(() => {
        const fetchFloorData = async () => {
            try {
            const response = await fetch(MULTIPLE_FLOORS_API, {
                method: "POST",
                headers: {
                "Content-Type": "application/json",
                },
                body: JSON.stringify({
                floor_plan: "",
                start_location: origin, // Using the input values
                end_location: destination, // Using the input values
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to fetch floor data");
            }

            const data = await response.json();
            const updatedImages = [];

            for (const path of data.path_list) {
                const intraFloorData = {
                    floor_plan: path.floorplan,
                    start_location: path["start location"],
                    end_location: path["end location"],
                };
                const imageSource = await fetchFloorImage(intraFloorData);
                    updatedImages.push({
                        image_data: imageSource,
                        text: `Start: ${intraFloorData.start_location}, End: ${intraFloorData.end_location}`,
                    }
                );
            }

            setImages(updatedImages);
            } catch (error) {
            console.error("Error fetching floor data:", error);
            }
        };

        const fetchFloorImage = async (intraData) => {
            try {
            const response = await fetch(SINGLE_FLOOR_API, {
                method: "POST",
                headers: {
                "Content-Type": "application/json",
                },
                body: JSON.stringify(intraData),
            });

            if (!response.ok) {
                throw new Error("Failed to fetch floor image");
            }

            const data = await response.json();
            const source = data.image;
            return source;
            } catch (error) {
            console.error("Error fetching floor image:", error);
            }
        };

        fetchFloorData();
        }, [origin, destination]);
    

    return (
        <div className="isolate bg-white">
            <nav className="flex h-9 items-center justify-between" aria-label="Global">
                <div className="flex lg:min-w-0 lg:flex-1" aria-label="Global">
                    <Link href="/" className="-m-1.5 p-1.5">
                        <span className="sr-only">FindYourWay</span>
                        <Image height={32} width={32} src={logoImg} alt="FindYourWay Logo" />
                    </Link>
                </div>
                <div className="hidden lg:flex lg:min-w-0 lg:flex-1 lg:justify-end lg:space-x-12">
                    {navigation.map((item) => (
                        <Link key={item.name} href={item.href} className="font-semibold text-gray-900 hover:text-gray-900">
                            {item.name}
                        </Link>
                    ))}
                </div>
            </nav>
            <div className="flex h-screen">
                <div className="w-2/5">
                    <div className="mt-10 flex flex-col">
                        <div className="px-4 sm:px-6">
                            <div className="px-4 sm:px-0">
                                <h3 className="text-lg font-medium leading-6 text-gray-900">Navigation Details</h3>
                                <p className="mt-1 text-sm text-gray-600">Where would you like to go?</p>
                            </div>
                        </div>
                        <div className="mt-5 md:mt-0">
                            <div>
                                <div className="overflow-hidden shadow sm:rounded-md">
                                    <div className="px-4 py-5 sm:p-6 space-y-3">
                                        <div className="relative mt-1">
                                            <label htmlFor="origin" className="block text-sm font-medium text-gray-700">
                                                Origin
                                            </label>
                                            <input
                                                onChange={(e) => setOrigin(e.target.value)}
                                                type="text"
                                                name="origin"
                                                id="origin"
                                                autoComplete="given-name"
                                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                            />
                                        </div>
                                        <div className="">
                                            <label htmlFor="destination" className="block text-sm font-medium text-gray-700">
                                                Destination
                                            </label>
                                            <input
                                                onChange={(e) => setDestination(e.target.value)}
                                                type="text"
                                                name="destination"
                                                id="destination"
                                                autoComplete="family-name"
                                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                            />
                                        </div>
                                    </div>
                                    <div className="bg-gray-50 px-4 py-3 sm:px-6">
                                        <button
                                            onClick={fetchImages}
                                            type="submit"
                                            className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                                        >
                                            Get directions
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="w-1 border-r border-gray-200" />
                <div className="w-full">
                    <Carousel>
                        {images.map(({ image_data: imageUri, text }) => (
                            <div key={imageUri}>
                                <img src={imageUri} alt="Floor Plan" />
                                <p>{text}</p>
                            </div>
                        ))}
                    </Carousel>
                </div>
            </div>
        </div>
    )
}