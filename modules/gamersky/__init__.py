# from graia.application import GraiaMiraiApplication, MessageChain
# from graia.application.event.messages import Group, GroupMessage, Member,FriendMessage,Friend
# from graia.application.exceptions import AccountMuted
# from graia.application.message.elements.internal import Plain, Image
# from graia.saya import Saya, Channel
# from graia.saya.builtins.broadcast import ListenerSchema
# from graia.application.message.parser.kanata import Kanata
# from graia.application.message.parser.signature import RegexMatch
# from modules.gamersky.gamersky_sub import getPicByType, fetchPage
#
# # 插件信息
# __name__ = "Gamersky_information"
# __description__ = "投喂Gamersky美图"
# __author__ = "JINO"
# __usage__ = "使用方法：lyf [type]"
#
# saya = Saya.current()
# channel = Channel.current()
#
# channel.name(__name__)
# channel.author(__author__)
# channel.description(f"{__description__}\n{__usage__}")
#
#
# @channel.use(ListenerSchema(
#     listening_events=[GroupMessage],
#     inline_dispatchers=[Kanata([RegexMatch('lyf .*')])]
# ))
# async def handle_command(
#         app: GraiaMiraiApplication,
#         message: MessageChain,
#         group: Group
# ):
#     try:
#         display__split = message.asDisplay().split(" ")
#         if len(display__split) > 2:
#             await app.sendGroupMessage(group, MessageChain.create([Plain(__usage__)]))
#             return
#         showType = ''
#         if len(display__split) == 2:
#             showType = display__split[1]
#         await app.sendGroupMessage(group, MessageChain.create([Image.fromLocalFile(getPicByType(showType))]))
#     except ValueError:
#         try:
#             await app.sendGroupMessage(group, MessageChain.create([Plain(__usage__)]))
#         except AccountMuted:
#             pass
#
#
# @channel.use(ListenerSchema(
#     listening_events=[FriendMessage],
#     inline_dispatchers=[Kanata([RegexMatch('gs-fetch .* .*')])]
# ))
# async def handle_command(
#         app: GraiaMiraiApplication,
#         message: MessageChain,
#         friend: Friend
# ):
#     try:
#         display__split = message.asDisplay().split(" ")
#         if len(display__split) > 3:
#             await app.sendFriendMessage(friend, MessageChain.create([Plain(__usage__)]))
#             return
#         comm1 = ''
#         comm2 = '1'
#         if len(display__split) == 2:
#             comm1 = display__split[1]
#         elif len(display__split) == 3:
#             comm1 = display__split[1]
#             comm2 = display__split[2]
#         count = fetchPage(comm2)
#         await app.sendFriendMessage(friend, MessageChain.create([Plain(f'fetch article count:{count}')]))
#     except ValueError:
#         try:
#             await app.sendFriendMessage(friend, MessageChain.create([Plain(__usage__)]))
#         except AccountMuted:
#             pass