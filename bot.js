const { Client, GatewayIntentBits, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, StringSelectMenuBuilder, ModalBuilder, TextInputBuilder, TextInputStyle } = require('discord.js');
require('dotenv').config();

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildPresences
    ]
});

// Store user responses
const userResponses = new Map();

// YOUR CUSTOM ROLE CONFIGURATION
const ROLE_CONFIG = {
    // GUILDS - Choose ONE only, cannot change
    guilds: {
        'VGD': 'VGD',
        'TRY': 'TRY', 
        'MVP': 'MVP',
        'VNT': 'VNT',
        'CSD': 'CSD',
        'SYN': 'SYN',
        'WR1': 'WR1',
        'KFH': 'KFH'
    },
    
    // TROOP TYPES - Choose ONE, can change anytime
    troops: {
        'Horde': 'Horde',
        'League': 'League',
        'Nature': 'Nature'
    },
    
    // LANGUAGES - Choose MULTIPLE
    languages: {
        'Chinese': 'Chinese',
        'English': 'English',
        'Japanese': 'Japanese',
        'Korean': 'Korean'
    },
    
    // NOTIFICATIONS - Choose MULTIPLE
    notifications: {
        'Announcements': 'Announcements',
        'Tournaments': 'Tournaments', 
        'Giveaways': 'Giveaways'
    },
    
    // SERVER RANGE - Choose ONE
    servers: {
        '1-107': 'Server 1-107',
        '108-224': 'Server 108-224',
        '225+': '225+'
    }
};

// REGISTER SLASH COMMANDS ON STARTUP
client.once('ready', async () => {
    console.log(`✅ Bot online as ${client.user.tag}`);
    
    const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);
    
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
        },
        {
            name: 'help',
            description: 'Show bot commands'
        }
    ];
    
    try {
        // Use YOUR CLIENT_ID
        const clientId = '1466070944211800246';
        
        console.log(`🔄 Force registering commands for ${clientId}...`);
        
        // Register GLOBALLY
        await rest.put(
            Routes.applicationCommands(clientId),
            { body: commands }
        );
        
        console.log('✅ Global commands registered!');
        
        // ALSO register for your specific server (faster)
        // REPLACE 'YOUR_SERVER_ID' with your actual server ID
        const guildId = 'YOUR_SERVER_ID'; // ← CHANGE THIS!
        
        if (guildId && guildId !== 'YOUR_SERVER_ID') {
            await rest.put(
                Routes.applicationGuildCommands(clientId, guildId),
                { body: commands }
            );
            console.log(`✅ Server-specific commands registered for: ${guildId}`);
            console.log('💡 Slash commands should appear INSTANTLY now!');
        } else {
            console.log('⚠️  Add your SERVER_ID to get instant commands');
            console.log('💡 Right-click your server → Copy ID');
        }
        
    } catch (error) {
        console.error('❌ Error:', error);
    }
});
// Remove old role and assign new one
async function updateRole(userId, guild, roleName, roleType) {
    try {
        const member = await guild.members.fetch(userId);
        if (!member) return false;
        
        // Get all possible roles of this type
        const allRoleNames = Object.values(ROLE_CONFIG[roleType]);
        
        // Remove old roles of same type
        for (const oldRoleName of allRoleNames) {
            const oldRole = guild.roles.cache.find(r => r.name === oldRoleName);
            if (oldRole && member.roles.cache.has(oldRole.id)) {
                await member.roles.remove(oldRole.id);
                console.log(`Removed ${oldRoleName} from ${member.user.tag}`);
            }
        }
        
        // Add new role
        const newRole = guild.roles.cache.find(r => r.name === roleName);
        if (newRole) {
            await member.roles.add(newRole.id);
            console.log(`Added ${roleName} to ${member.user.tag}`);
            return true;
        }
        
        return false;
    } catch (error) {
        console.error('❌ Error updating role:', error);
        return false;
    }
}

// Assign multiple roles (for languages, notifications)
async function assignMultipleRoles(userId, guild, roleNames, roleType) {
    try {
        const member = await guild.members.fetch(userId);
        if (!member) return;
        
        for (const roleName of roleNames) {
            const role = guild.roles.cache.find(r => r.name === roleName);
            if (role && !member.roles.cache.has(role.id)) {
                await member.roles.add(role.id);
                console.log(`Added ${roleName} to ${member.user.tag}`);
            }
        }
    } catch (error) {
        console.error('❌ Error assigning multiple roles:', error);
    }
}

// Handle slash commands
client.on('interactionCreate', async interaction => {
    if (!interaction.isCommand()) return;
    
    const { commandName, user, guild } = interaction;
    
    if (commandName === 'setup') {
        // Check if user already has a guild (cannot change)
        const responses = userResponses.get(user.id) || {};
        if (responses.guild) {
            const embed = new EmbedBuilder()
                .setColor(0xFF0000)
                .setTitle('❌ Already in a Guild')
                .setDescription(`You are already in **${responses.guild}** guild.\n\n**Guild selection cannot be changed.**\n\nUse \`/changetroop\` to change your troop type.\nUse \`/myprofile\` to view your roles.`);
            
            return interaction.reply({ embeds: [embed], ephemeral: true });
        }
        
        // Start setup: Question 1 - GUILD SELECTION
        const embed = new EmbedBuilder()
            .setColor(0x5865F2)
            .setTitle('🏰 Guild Selection')
            .setDescription('**Choose your guild (CANNOT BE CHANGED):**\n\nVGD, TRY, MVP, VNT\nCSD, SYN, WR1, KFH')
            .setFooter({ text: 'This choice is permanent!' });
        
        const selectMenu = new StringSelectMenuBuilder()
            .setCustomId('select_guild')
            .setPlaceholder('Choose your guild...')
            .setMinValues(1)
            .setMaxValues(1)
            .addOptions([
                { label: 'VGD', value: 'VGD', emoji: '🛡️' },
                { label: 'TRY', value: 'TRY', emoji: '⚔️' },
                { label: 'MVP', value: 'MVP', emoji: '🏆' },
                { label: 'VNT', value: 'VNT', emoji: '🌀' },
                { label: 'CSD', value: 'CSD', emoji: '⚡' },
                { label: 'SYN', value: 'SYN', emoji: '💎' },
                { label: 'WR1', value: 'WR1', emoji: '👑' },
                { label: 'KFH', value: 'KFH', emoji: '🔥' }
            ]);
        
        const row = new ActionRowBuilder().addComponents(selectMenu);
        
        await interaction.reply({ 
            embeds: [embed], 
            components: [row],
            ephemeral: true 
        });
    }
    
    if (commandName === 'myprofile') {
        const responses = userResponses.get(user.id) || {};
        const member = await guild.members.fetch(user.id);
        const userRoles = member.roles.cache
            .filter(role => 
                Object.values(ROLE_CONFIG.guilds).includes(role.name) ||
                Object.values(ROLE_CONFIG.troops).includes(role.name) ||
                Object.values(ROLE_CONFIG.languages).includes(role.name) ||
                Object.values(ROLE_CONFIG.notifications).includes(role.name) ||
                Object.values(ROLE_CONFIG.servers).includes(role.name)
            )
            .map(role => role.name);
        
        const embed = new EmbedBuilder()
            .setColor(0x5865F2)
            .setTitle('👤 Your Profile')
            .setThumbnail(user.displayAvatarURL())
            .addFields(
                { name: '🏰 Guild', value: responses.guild || 'Not selected', inline: true },
                { name: '⚔️ Troop Type', value: responses.troopType || 'Not selected', inline: true },
                { name: '🌍 Server Range', value: responses.serverRange || 'Not selected', inline: true },
                { name: '🗣️ Languages', value: responses.languages?.join(', ') || 'None', inline: false },
                { name: '🔔 Notifications', value: responses.notifications?.join(', ') || 'None', inline: false },
                { name: '📋 Current Roles', value: userRoles.join(', ') || 'None', inline: false }
            );
        
        await interaction.reply({ embeds: [embed], ephemeral: true });
    }
    
    if (commandName === 'changetroop') {
        const embed = new EmbedBuilder()
            .setColor(0x5865F2)
            .setTitle('⚔️ Change Troop Type')
            .setDescription('Choose your new troop type:');
        
        const row = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('change_horde')
                    .setLabel('Horde')
                    .setStyle(ButtonStyle.Primary)
                    .setEmoji('⚔️'),
                new ButtonBuilder()
                    .setCustomId('change_league')
                    .setLabel('League')
                    .setStyle(ButtonStyle.Primary)
                    .setEmoji('🏅'),
                new ButtonBuilder()
                    .setCustomId('change_nature')
                    .setLabel('Nature')
                    .setStyle(ButtonStyle.Primary)
                    .setEmoji('🌿')
            );
        
        await interaction.reply({ 
            embeds: [embed], 
            components: [row],
            ephemeral: true 
        });
    }
});

// Handle select menus
client.on('interactionCreate', async interaction => {
    if (!interaction.isStringSelectMenu()) return;
    
    const { customId, user, guild, values } = interaction;
    const userId = user.id;
    
    if (!userResponses.has(userId)) {
        userResponses.set(userId, {});
    }
    
    const responses = userResponses.get(userId);
    
    // GUILD SELECTION (Question 1)
    if (customId === 'select_guild') {
        const selectedGuild = values[0];
        responses.guild = selectedGuild;
        
        // Assign guild role (cannot change)
        await updateRole(userId, guild, selectedGuild, 'guilds');
        
        // Question 2: TROOP TYPE
        const embed = new EmbedBuilder()
            .setColor(0x5865F2)
            .setTitle('⚔️ Troop Type')
            .setDescription(`**Guild:** ${selectedGuild}\n\nChoose your troop type:\n\n⚔️ Horde - Strong attackers\n🏅 League - Balanced fighters\n🌿 Nature - Support specialists\n\n*You can change this later using \`/changetroop\`*`);
        
        const row = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('troop_horde')
                    .setLabel('Horde')
                    .setStyle(ButtonStyle.Primary)
                    .setEmoji('⚔️'),
                new ButtonBuilder()
                    .setCustomId('troop_league')
                    .setLabel('League')
                    .setStyle(ButtonStyle.Primary)
                    .setEmoji('🏅'),
                new ButtonBuilder()
                    .setCustomId('troop_nature')
                    .setLabel('Nature')
                    .setStyle(ButtonStyle.Primary)
                    .setEmoji('🌿')
            );
        
        await interaction.update({ 
            embeds: [embed], 
            components: [row] 
        });
    }
    
    // LANGUAGES SELECTION (Question 4)
    if (customId === 'select_languages') {
        responses.languages = values;
        await assignMultipleRoles(userId, guild, values, 'languages');
        
        // Question 5: NOTIFICATIONS
        const embed = new EmbedBuilder()
            .setColor(0x5865F2)
            .setTitle('🔔 Notifications')
            .setDescription('Select notification types you want to receive:');
        
        const selectMenu = new StringSelectMenuBuilder()
            .setCustomId('select_notifications')
            .setPlaceholder('Choose notifications...')
            .setMinValues(0)
            .setMaxValues(3)
            .addOptions([
                { label: 'Announcements', value: 'Announcements', emoji: '📢' },
                { label: 'Tournaments', value: 'Tournaments', emoji: '🏆' },
                { label: 'Giveaways', value: 'Giveaways', emoji: '🎁' }
            ]);
        
        const row = new ActionRowBuilder().addComponents(selectMenu);
        
        await interaction.update({ 
            embeds: [embed], 
            components: [row] 
        });
    }
    
    // NOTIFICATIONS SELECTION (Question 5)
    if (customId === 'select_notifications') {
        responses.notifications = values;
        await assignMultipleRoles(userId, guild, values, 'notifications');
        
        // Question 6: SERVER RANGE
        const embed = new EmbedBuilder()
            .setColor(0x5865F2)
            .setTitle('🌍 Server Range')
            .setDescription('Select your main account server range:');
        
        const row = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('server_1_107')
                    .setLabel('Server 1-107')
                    .setStyle(ButtonStyle.Secondary),
                new ButtonBuilder()
                    .setCustomId('server_108_224')
                    .setLabel('Server 108-224')
                    .setStyle(ButtonStyle.Secondary),
                new ButtonBuilder()
                    .setCustomId('server_225')
                    .setLabel('Server 225+')
                    .setStyle(ButtonStyle.Secondary)
            );
        
        await interaction.update({ 
            embeds: [embed], 
            components: [row] 
        });
    }
});

// Handle button interactions
client.on('interactionCreate', async interaction => {
    if (!interaction.isButton()) return;
    
    const { customId, user, guild } = interaction;
    const userId = user.id;
    
    if (!userResponses.has(userId)) {
        userResponses.set(userId, {});
    }
    
    const responses = userResponses.get(userId);
    
    // TROOP TYPE selection during setup
    if (customId.startsWith('troop_')) {
        const troopType = customId.replace('troop_', '').charAt(0).toUpperCase() + 
                         customId.replace('troop_', '').slice(1);
        responses.troopType = troopType;
        
        // Assign troop role
        await updateRole(userId, guild, troopType, 'troops');
        
        // Question 3: LANGUAGES
        const embed = new EmbedBuilder()
            .setColor(0x5865F2)
            .setTitle('🗣️ Languages')
            .setDescription(`**Troop:** ${troopType}\n\nSelect languages you speak:`);
        
        const selectMenu = new StringSelectMenuBuilder()
            .setCustomId('select_languages')
            .setPlaceholder('Choose languages...')
            .setMinValues(0)
            .setMaxValues(4)
            .addOptions([
                { label: 'Chinese', value: 'Chinese', emoji: '🔤' },
                { label: 'English', value: 'English', emoji: '📜' },
                { label: 'Japanese', value: 'Japanese', emoji: '🇯🇵' },
                { label: 'Korean', value: 'Korean', emoji: '🇰🇷' }
            ]);
        
        const row = new ActionRowBuilder().addComponents(selectMenu);
        
        await interaction.update({ 
            embeds: [embed], 
            components: [row] 
        });
    }
    
    // CHANGE TROOP TYPE command
    if (customId.startsWith('change_')) {
        const troopType = customId.replace('change_', '').charAt(0).toUpperCase() + 
                         customId.replace('change_', '').slice(1);
        
        responses.troopType = troopType;
        await updateRole(userId, guild, troopType, 'troops');
        
        const embed = new EmbedBuilder()
            .setColor(0x3BA55C)
            .setTitle('✅ Troop Type Updated')
            .setDescription(`Your troop type has been changed to **${troopType}**`)
            .setFooter({ text: 'Use /myprofile to view all your roles' });
        
        await interaction.update({ 
            embeds: [embed], 
            components: [] 
        });
    }
    
    // SERVER RANGE selection (final step)
    if (customId.startsWith('server_')) {
        let serverRange = '';
        if (customId === 'server_1_107') serverRange = '1-107';
        if (customId === 'server_108_224') serverRange = '108-224';
        if (customId === 'server_225') serverRange = '225+';
        
        responses.serverRange = serverRange;
        
        // Assign server role
        await updateRole(userId, guild, ROLE_CONFIG.servers[serverRange], 'servers');
        
        // COMPLETION MESSAGE
        const embed = new EmbedBuilder()
            .setColor(0x3BA55C)
            .setTitle('✅ Setup Complete!')
            .setDescription(`**Welcome to ${responses.guild}!**\n\nYour roles have been assigned:\n\n🏰 **Guild:** @${responses.guild}\n⚔️ **Troop:** @${responses.troopType}\n🌍 **Server:** @${serverRange}\n🗣️ **Languages:** ${responses.languages?.map(l => `@${l}`).join(', ') || 'None'}\n🔔 **Notifications:** ${responses.notifications?.map(n => `@${n}`).join(', ') || 'None'}`)
            .setFooter({ text: 'Use /changetroop to change your troop type anytime!' });
        
        await interaction.update({ 
            embeds: [embed], 
            components: [] 
        });
    }
});

client.login(process.env.DISCORD_TOKEN).catch(error => {
    console.error('❌ Login failed:', error.message);
    process.exit(1);
});