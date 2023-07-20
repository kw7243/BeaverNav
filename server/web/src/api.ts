interface RouteResponse {
    text: string,
    image_filepath: string,
}

export async function sendRoutingRequest(origin: string, destination: string): Promise<RouteResponse[] | undefined> {
    const response = await fetch('http://45.33.64.67/route', {
        method: 'POST',
        headers: new Headers({
            'Content-Type': 'application/json',
        }),
        body: JSON.stringify({
            origin,
            destination,
        })
    })

    if (response.ok) {
        return await response.json()
    }

    console.error(`Got an error when requesting the route: ${await response.text()}`)
    return undefined
}

export async function getRouteImage(image_file_location: string): Promise<string | undefined> {
    const response = await fetch(`http://45.33.64.67/route/image/?path="${image_file_location}"`)
    if (response.ok) {
        const blob = await response.blob()
        return URL.createObjectURL(blob)
    }

    console.error(`Got an error when requesting the image for route: ${await response.text()}`)
    return undefined
}