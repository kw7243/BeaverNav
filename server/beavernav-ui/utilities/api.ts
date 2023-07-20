export interface RouteResponse {
    text: string,
    image_data: string,
}

export async function sendRoutingRequest(origin: string, destination: string): Promise<RouteResponse[] | undefined> {
    console.log(origin, destination)
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