# nudge-bot

`pip install git+https://github.com/Nudge-Security/nudge-bot.git `

Note: Get refresh token from local storage in your browser - CognitoIdentityServiceProvider.*.*.refreshToken;

Usage: 
    
    nudge-bot [OPTIONS] COMMAND [ARGS]...;

Options:

    --refresh-token TEXT  Refresh token for authentication (Set environment variable to REFRESH_TOKEN)

    --help                Show this message and exit.

Commands:
  
    bulk-set-app-field      Set a field for list of apps

    create-field            Create a field

    list-fields             List all of the fields for your organization

    search-app              Search for an app

    set-app-field           Set a field for a given app

    supply-chain            Search for the supply chain of a given app

    transform-app-list      Transform list of app names or domains to internal identifier

    update-field            Update a field
`