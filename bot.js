const { Client, GatewayIntentBits, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, StringSelectMenuBuilder } = require('discord.js');
require('dotenv').config();

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.MessageContent
    ]
});

// Store user setups
const userSetups = new Map();

// === EXACT INTERFACE FROM YOUR SCREENSHOTS ===

// Command: !customize - Shows the exact interface
client.on('messageCreate', async message => {
    if (message.author.bot) return;
    
    // Start customization
    if (message.content.toLowerCase() === '!customize') {
        const userId = message.author.id;
        
        // Initialize user setup
        userSetups.set(userId, {
            step: 1,
            favoriteSet: '',
            notifications: [],
            troopType: '',
            languages: [],
            serverRange: ''
        });
        
        // Show the exact interface from screenshot 1
        await showCustomizationInterface(message, userId);
    }
    
    // Show all channels
    if (message.content.toLowerCase() === '!channels') {
        await showAllChannels(message);
    }
    
    // Show answers
    if (message.content.toLowerCase() === '!answers') {
        await showAnswers(message);
    }
});

// Show the exact customization interface
async function showCustomizationInterface(message, userId) {
    const setup = userSetups.get(userId);
    
    // Create the embed that looks exactly like your screenshot
    const embed = new EmbedBuilder()
        .setColor(0x2f3136) // Discord dark gray
        .setTitle('Channels & Roles')
        .setDescription('```\nCustomize    All Channels\n```')
        .addFields(
            { 
                name: 'Customization Questions', 
                value: 'Answer questions to get access to more channels and roles.\n\u200b',
                inline: false 
            }
        );
    
    // Step 1: Favorite Set Question
    if (setup.step === 1) {
        embed.addFields(
            { 
                name: "What's your favorite set? *", 
                value: '```\n' + (setup.favoriteSet || 'Type your answer...') + '\n```\n\u200b',
                inline: false 
            }
        );
        
        if (setup.favoriteSet) {
            embed.addFields(
                { 
                    name: 'Role Assignment', 
                    value: `You will receive the **@${setup.favoriteSet}** role.\n\u200b`,
                    inline: false 
                }
            );
        }
        
        const row = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('next_step')
                    .setLabel('Next Question')
                    .setStyle(ButtonStyle.Primary)
                    .setEmoji('➡️')
            );
        
        // Send with input field simulation
        const row2 = new ActionRowBuilder()
            .addComponents(
                new StringSelectMenuBuilder()
                    .setCustomId('select_set')
                    .setPlaceholder('Select or type your favorite set...')
                    .addOptions([
                        { label: 'Deluxe ex', value: 'Deluxe ex', emoji: '🎮' },
                        { label: 'Basic Set', value: 'Basic Set', emoji: '🔰' },
                        { label: 'Premium Set', value: 'Premium Set', emoji: '💎' },
                        { label: 'Custom...', value: 'custom', emoji: '✏️' }
                    ])
            );
        
        await message.reply({ 
            embeds: [embed], 
            components: [row2, row] 
        });
    }
    
    // Step 2: Notifications Question
    else if (setup.step === 2) {
        embed.addFields(
            { 
                name: "Would you like to receive ping notifications?", 
                value: '\u200b',
                inline: false 
            }
        );
        
        const selected = setup.notifications || [];
        const announcements = selected.includes('Announcements') ? '✅' : '⬜';
        const tournaments = selected.includes('Tournaments') ? '✅' : '⬜';
        const giveaways = selected.includes('Giveaways') ? '✅' : '⬜';
        
        embed.addFields(
            { 
                name: 'Options', 
                value: `${announcements} **Announcements**\n${tournaments} **Tournaments**\n${giveaways} **Giveaways**\n\u200b`,
                inline: false 
            }
        );
        
        // Calculate role info
        const notificationCount = setup.notifications.length;
        const roleInfo = `You will receive the ${notificationCount > 0 ? '**@Announcements**, **@Tournaments**, ' : ''}${notificationCount === 3 ? 'and **1 other** role.' : notificationCount === 2 ? 'and **1 other** role.' : '**1 other** role.'}`;
        
        embed.addFields(
            { 
                name: 'Role Assignment', 
                value: roleInfo + '\n\u200b',
                inline: false 
            }
        );
        
        const row = new ActionRowBuilder()
            .addComponents(
                new StringSelectMenuBuilder()
                    .setCustomId('select_notifications')
                    .setPlaceholder('Select notification types...')
                    .setMinValues(0)
                    .setMaxValues(3)
                    .addOptions([
                        { label: 'Announcements', value: 'Announcements', emoji: '📢' },
                        { label: 'Tournaments', value: 'Tournaments', emoji: '🏆' },
                        { label: 'Giveaways', value: 'Giveaways', emoji: '🎁' }
                    ])
            );
        
        const row2 = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('prev_step')
                    .setLabel('Previous')
                    .setStyle(ButtonStyle.Secondary),
                new ButtonBuilder()
                    .setCustomId('next_step')
                    .setLabel('Next Question')
                    .setStyle(ButtonStyle.Primary)
                    .setEmoji('➡️')
            );
        
        await message.reply({ 
            embeds: [embed], 
            components: [row, row2] 
        });
    }
    
    // Step 3: Troop Type Question (EXACTLY like screenshot 3)
    else if (setup.step === 3) {
        embed.addFields(
            { 
                name: "Please select your main troop type *", 
                value: '\u200b',
                inline: false 
            }
        );
        
        const horde = setup.troopType === 'Horde' ? '🔘' : '⚪';
        const league = setup.troopType === 'League' ? '🔘' : '⚪';
        const nature = setup.troopType === 'Nature' ? '🔘' : '⚪';
        
        embed.addFields(
            { 
                name: 'Options', 
                value: `${horde} **⚔ Horde**\n${league} **🏅 League**\n${nature} **🌿 Nature**\n\u200b`,
                inline: false 
            }
        );
        
        if (setup.troopType) {
            embed.addFields(
                { 
                    name: 'Role Assignment', 
                    value: `You will receive the **@${setup.troopType}** role.\n\u200b`,
                    inline: false 
                }
            );
        }
        
        const row = new ActionRowBuilder()
            .addComponents(
                new StringSelectMenuBuilder()
                    .setCustomId('select_troop')
                    .setPlaceholder('Select your troop type...')
                    .setMinValues(1)
                    .setMaxValues(1)
                    .addOptions([
                        { label: 'Horde', value: 'Horde', emoji: '⚔️' },
                        { label: 'League', value: 'League', emoji: '🏅' },
                        { label: 'Nature', value: 'Nature', emoji: '🌿' }
                    ])
            );
        
        const row2 = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('prev_step')
                    .setLabel('Previous')
                    .setStyle(ButtonStyle.Secondary),
                new ButtonBuilder()
                    .setCustomId('next_step')
                    .setLabel('Next Question')
                    .setStyle(ButtonStyle.Primary)
                    .setEmoji('➡️')
            );
        
        await message.reply({ 
            embeds: [embed], 
            components: [row, row2] 
        });
    }
    
    // Step 4: Languages Question
    else if (setup.step === 4) {
        embed.addFields(
            { 
                name: "Please select any languages you speak *", 
                value: '\u200b',
                inline: false 
            }
        );
        
        const selected = setup.languages || [];
        const chinese = selected.includes('Chinese') ? '✅' : '⬜';
        const english = selected.includes('English') ? '✅' : '⬜';
        const japanese = selected.includes('Japanese') ? '✅' : '⬜';
        const korean = selected.includes('Korean') ? '✅' : '⬜';
        
        embed.addFields(
            { 
                name: 'Options', 
                value: `${chinese} **🔤 Chinese**\n${english} **📜 English**\n${japanese} **🇯🇵 Japanese**\n${korean} **🇰🇷 Korean**\n\u200b`,
                inline: false 
            }
        );
        
        // Calculate role info
        const languageCount = setup.languages.length;
        const otherCount = Math.max(0, languageCount - 2);
        const roleInfo = languageCount > 0 
            ? `You will receive the **@Chinese - 繁體中文**, **@English**${otherCount > 0 ? `, and **${otherCount} other** roles.` : ' roles.'}`
            : 'You will not receive any language roles.';
        
        embed.addFields(
            { 
                name: 'Role Assignment', 
                value: roleInfo + '\n\u200b',
                inline: false 
            }
        );
        
        const row = new ActionRowBuilder()
            .addComponents(
                new StringSelectMenuBuilder()
                    .setCustomId('select_languages')
                    .setPlaceholder('Select languages...')
                    .setMinValues(0)
                    .setMaxValues(4)
                    .addOptions([
                        { label: 'Chinese', value: 'Chinese', emoji: '🔤' },
                        { label: 'English', value: 'English', emoji: '📜' },
                        { label: 'Japanese', value: 'Japanese', emoji: '🇯🇵' },
                        { label: 'Korean', value: 'Korean', emoji: '🇰🇷' }
                    ])
            );
        
        const row2 = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('prev_step')
                    .setLabel('Previous')
                    .setStyle(ButtonStyle.Secondary),
                new ButtonBuilder()
                    .setCustomId('next_step')
                    .setLabel('Next Question')
                    .setStyle(ButtonStyle.Primary)
                    .setEmoji('➡️')
            );
        
        await message.reply({ 
            embeds: [embed], 
            components: [row, row2] 
        });
    }
    
    // Step 5: Server Range Question
    else if (setup.step === 5) {
        embed.addFields(
            { 
                name: "Please select the server range of your main account *", 
                value: '\u200b',
                inline: false 
            }
        );
        
        const server1 = setup.serverRange === '1-107' ? '🔘' : '⚪';
        const server2 = setup.serverRange === '108-224' ? '🔘' : '⚪';
        const server3 = setup.serverRange === '225+' ? '🔘' : '⚪';
        
        embed.addFields(
            { 
                name: 'Options', 
                value: `${server1} **Server 1 - Server 107**\n${server2} **Server 108 - Server 224**\n${server3} **Server 225 or Above**\n\u200b`,
                inline: false 
            }
        );
        
        if (setup.serverRange) {
            const roleName = setup.serverRange === '225+' ? '225+' : setup.serverRange;
            embed.addFields(
                { 
                    name: 'Role Assignment', 
                    value: `You will receive the **@${roleName}** role.\n\u200b`,
                    inline: false 
                }
            );
        }
        
        const row = new ActionRowBuilder()
            .addComponents(
                new StringSelectMenuBuilder()
                    .setCustomId('select_server')
                    .setPlaceholder('Select server range...')
                    .setMinValues(1)
                    .setMaxValues(1)
                    .addOptions([
                        { label: 'Server 1-107', value: '1-107' },
                        { label: 'Server 108-224', value: '108-224' },
                        { label: 'Server 225+', value: '225+' }
                    ])
            );
        
        const row2 = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('prev_step')
                    .setLabel('Previous')
                    .setStyle(ButtonStyle.Secondary),
                new ButtonBuilder()
                    .setCustomId('complete_setup')
                    .setLabel('Complete Setup')
                    .setStyle(ButtonStyle.Success)
                    .setEmoji('✅')
            );
        
        await message.reply({ 
            embeds: [embed], 
            components: [row, row2] 
        });
    }
}

// Show all channels interface
async function showAllChannels(message) {
    const embed = new EmbedBuilder()
        .setColor(0x2f3136)
        .setTitle('Channels & Roles')
        .setDescription('```\nCustomize    All Channels\n```')
        .addFields(
            { 
                name: 'Available Channels', 
                value: 'Browse all channels in the server:\n\u200b',
                inline: false 
            },
            { 
                name: '📢 Announcements', 
                value: 'Requires: @Announcements role',
                inline: true 
            },
            { 
                name: '🏆 Tournaments', 
                value: 'Requires: @Tournaments role',
                inline: true 
            },
            { 
                name: '🎁 Giveaways', 
                value: 'Requires: @Giveaways role',
                inline: true 
            },
            { 
                name: '⚔️ Horde Chat', 
                value: 'Requires: @Horde role',
                inline: true 
            },
            { 
                name: '🏅 League Chat', 
                value: 'Requires: @League role',
                inline: true 
            },
            { 
                name: '🌿 Nature Chat', 
                value: 'Requires: @Nature role',
                inline: true 
            }
        );
    
    await message.reply({ embeds: [embed] });
}

// Show answers interface
async function showAnswers(message) {
    const userId = message.author.id;
    const setup = userSetups.get(userId) || {};
    
    const embed = new EmbedBuilder()
        .setColor(0x2f3136)
        .setTitle('Channels & Roles')
        .setDescription('```\nAnswers\n```')
        .addFields(
            { 
                name: 'Your Answers', 
                value: 'Here are your current selections:\n\u200b',
                inline: false 
            },
            { 
                name: 'Favorite Set', 
                value: setup.favoriteSet || 'Not answered',
                inline: true 
            },
            { 
                name: 'Troop Type', 
                value: setup.troopType || 'Not answered',
                inline: true 
            },
            { 
                name: 'Server Range', 
                value: setup.serverRange || 'Not answered',
                inline: true 
            },
            { 
                name: 'Languages', 
                value: (setup.languages || []).join(', ') || 'None',
                inline: false 
            },
            { 
                name: 'Notifications', 
                value: (setup.notifications || []).join(', ') || 'None',
                inline: false 
            }
        )
        .setFooter({ text: 'Use !customize to modify your answers' });
    
    await message.reply({ embeds: [embed] });
}

// Handle interactions
client.on('interactionCreate', async interaction => {
    if (!interaction.isStringSelectMenu() && !interaction.isButton()) return;
    
    const userId = interaction.user.id;
    const setup = userSetups.get(userId) || { step: 1 };
    
    // Handle favorite set selection
    if (interaction.isStringSelectMenu()) {
        if (interaction.customId === 'select_set') {
            const value = interaction.values[0];
            if (value === 'custom') {
                // Prompt for custom input
                await interaction.reply({ 
                    content: 'Please type your favorite set name:',
                    ephemeral: true 
                });
                
                // Create a message collector for custom input
                const filter = m => m.author.id === userId;
                const collector = interaction.channel.createMessageCollector({ 
                    filter, 
                    time: 30000,
                    max: 1 
                });
                
                collector.on('collect', async m => {
                    setup.favoriteSet = m.content;
                    userSetups.set(userId, setup);
                    await m.delete();
                    await showCustomizationInterface(interaction.message, userId);
                });
                
                return;
            }
            
            setup.favoriteSet = value;
            userSetups.set(userId, setup);
            await interaction.deferUpdate();
            await showCustomizationInterface(interaction.message, userId);
        }
        
        else if (interaction.customId === 'select_notifications') {
            setup.notifications = interaction.values;
            userSetups.set(userId, setup);
            await interaction.deferUpdate();
            await showCustomizationInterface(interaction.message, userId);
        }
        
        else if (interaction.customId === 'select_troop') {
            setup.troopType = interaction.values[0];
            userSetups.set(userId, setup);
            await interaction.deferUpdate();
            await showCustomizationInterface(interaction.message, userId);
        }
        
        else if (interaction.customId === 'select_languages') {
            setup.languages = interaction.values;
            userSetups.set(userId, setup);
            await interaction.deferUpdate();
            await showCustomizationInterface(interaction.message, userId);
        }
        
        else if (interaction.customId === 'select_server') {
            setup.serverRange = interaction.values[0];
            userSetups.set(userId, setup);
            await interaction.deferUpdate();
            await showCustomizationInterface(interaction.message, userId);
        }
    }
    
    // Handle button clicks
    if (interaction.isButton()) {
        if (interaction.customId === 'next_step') {
            setup.step = Math.min(setup.step + 1, 5);
            userSetups.set(userId, setup);
            await interaction.deferUpdate();
            await showCustomizationInterface(interaction.message, userId);
        }
        
        else if (interaction.customId === 'prev_step') {
            setup.step = Math.max(setup.step - 1, 1);
            userSetups.set(userId, setup);
            await interaction.deferUpdate();
            await showCustomizationInterface(interaction.message, userId);
        }
        
        else if (interaction.customId === 'complete_setup') {
            // Assign roles based on selections
            await assignRoles(interaction, setup);
            
            const embed = new EmbedBuilder()
                .setColor(0x3BA55C)
                .setTitle('✅ Setup Complete!')
                .setDescription('Your roles have been assigned based on your preferences.')
                .addFields(
                    { name: 'Favorite Set', value: `@${setup.favoriteSet}`, inline: true },
                    { name: 'Troop Type', value: `@${setup.troopType}`, inline: true },
                    { name: 'Server Range', value: `@${setup.serverRange}`, inline: true },
                    { name: 'Languages', value: setup.languages.map(l => `@${l}`).join(', ') || 'None', inline: false },
                    { name: 'Notifications', value: setup.notifications.map(n => `@${n}`).join(', ') || 'None', inline: false }
                );
            
            await interaction.update({ 
                embeds: [embed], 
                components: [] 
            });
        }
    }
});

// Assign roles to user
async function assignRoles(interaction, setup) {
    try {
        const member = await interaction.guild.members.fetch(interaction.user.id);
        const rolesToAdd = [];
        
        // Add favorite set role
        if (setup.favoriteSet) {
            const role = interaction.guild.roles.cache.find(r => r.name === setup.favoriteSet);
            if (role) rolesToAdd.push(role);
        }
        
        // Add troop role
        if (setup.troopType) {
            const role = interaction.guild.roles.cache.find(r => r.name === setup.troopType);
            if (role) rolesToAdd.push(role);
        }
        
        // Add language roles
        if (setup.languages && setup.languages.length > 0) {
            for (const lang of setup.languages) {
                const role = interaction.guild.roles.cache.find(r => r.name === lang);
                if (role) rolesToAdd.push(role);
            }
        }
        
        // Add notification roles
        if (setup.notifications && setup.notifications.length > 0) {
            for (const notif of setup.notifications) {
                const role = interaction.guild.roles.cache.find(r => r.name === notif);
                if (role) rolesToAdd.push(role);
            }
        }
        
        // Add server range role
        if (setup.serverRange) {
            const roleName = setup.serverRange === '225+' ? '225+' : `Server ${setup.serverRange}`;
            const role = interaction.guild.roles.cache.find(r => r.name === roleName);
            if (role) rolesToAdd.push(role);
        }
        
        // Assign all roles
        if (rolesToAdd.length > 0) {
            await member.roles.add(rolesToAdd);
            console.log(`✅ Assigned ${rolesToAdd.length} roles to ${member.user.tag}`);
        }
        
    } catch (error) {
        console.error('❌ Error assigning roles:', error);
    }
}

// Bot ready
client.once('ready', () => {
    console.log(`✅ Discord Interface Bot online as ${client.user.tag}`);
    console.log(`📱 Commands available:`);
    console.log(`   !customize - Show role setup interface`);
    console.log(`   !channels  - Show all available channels`);
    console.log(`   !answers   - View your current answers`);
});

// Login
client.login(process.env.DISCORD_TOKEN).catch(error => {
    console.error('❌ Login failed:', error.message);
    process.exit(1);
});