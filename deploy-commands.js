// deploy-commands.js
const { REST, Routes } = require('discord.js');
require('dotenv').config();

const commands = [
    {
        name: 'setup',
        description: 'Setup your guild and roles'
    },
    {
        name: 'myprofile',
        description: 'View your current roles'
    },
    {
        name: 'changetroop',
        description: 'Change your troop type'
    }
];

const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);

(async () => {
    try {
        console.log('🔄 Registering slash commands...');
        
        // You need to know your CLIENT_ID
        const clientId = process.env.CLIENT_ID; // Get from Discord Developer Portal
        
        if (!clientId) {
            console.error('❌ CLIENT_ID not found in .env file!');
            console.log('💡 Add CLIENT_ID=your_client_id to Railway Variables');
            return;
        }
        
        await rest.put(
            Routes.applicationCommands(clientId),
            { body: commands }
        );
        
        console.log('✅ Slash commands registered!');
        console.log('💡 Commands may take up to 1 hour to appear.');
        console.log('   To force refresh, restart Discord app.');
    } catch (error) {
        console.error('❌ Error:', error);
    }
})();