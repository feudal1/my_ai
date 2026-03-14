using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;

using cad_tools;
using System.Collections.Generic;
using System.Reflection;
using System.Linq;
using System.Text.Json;

namespace  tools
{
    partial class Program
    {
        static Dictionary<string, Action<string[]>>? commands;
        static SldWorks? swApp;
        static ModelDoc2? swModel;
        
        class CommandInfo
        {
          public string Name { get; set; } = "";
          public string? Description { get; set; }
          public string? Parameters { get; set; }
          public string? Group { get; set; }  // 命令所属组
          public Action<string[]> Action { get; set; } = null!;
        }
        
        static Dictionary<string, CommandInfo>? commandInfos;
        
        [STAThread]
        static void Main(string[] args)
        {
            RegisterCommands();

            // 仅导出命令信息时，不需要连接 SolidWorks（否则在未启动 SW 时会直接失败）
            if (args.Length > 0)
            {
                string command = args[0];
                
                if (command == "--export-commands")
                {
                    ExportCommandsToJson();
                    return;
                }
            }

            // 其余命令才需要连接 SolidWorks
            swApp = Connect.run();
            if (swApp == null)
            {
                Console.WriteLine("错误：无法连接到 SolidWorks 应用程序。");
                ShowHelp();
                return;
            }

            swModel = (ModelDoc2)swApp.ActiveDoc;

            if (args.Length > 0)
            {
                string command = args[0];

                if (commands != null && commands.ContainsKey(command))
                {
                    commands[command](args);
                }
                else
                {
                    Console.WriteLine($"没这命令：{command}");
                    ShowHelp();
                }
            }
            else
            {
                ShowHelp();
                ExportCommandsToJson();
            }
        }
        
       static void ExportCommandsToJson()
        {
            var exportData = new List<Dictionary<string, string?>>();
            
            if (commandInfos != null)
            {
                foreach (var cmd in commandInfos.Values.OrderBy(c => c.Name, StringComparer.OrdinalIgnoreCase))
                {
                    exportData.Add(new Dictionary<string, string?>
                    {
                        { "name", cmd.Name },
                        { "description", cmd.Description },
                        { "parameters", cmd.Parameters },
                        { "group", cmd.Group ?? "csharp" }  // 默认组为 "csharp"
                    });
                }
            }
            
            var options = new JsonSerializerOptions 
            { 
                WriteIndented = true,
                Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
            };
           string json = JsonSerializer.Serialize(exportData, options);
            
            // 写到可执行文件所在目录，便于 Python 直接读取/刷新
            var outputPath = Path.Combine(AppContext.BaseDirectory, "csharp_commands.json");
            // 避免 UTF-8 BOM，方便其他语言直接解析 JSON
            File.WriteAllText(outputPath, json, new System.Text.UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
            
           Console.WriteLine($"已导出 {exportData.Count} 个命令到：{outputPath}");
        }
        
       static void ShowHelp()
        {
           Console.WriteLine("\n可用命令:");
            if (commandInfos != null)
            {
                foreach (var cmd in commandInfos.Values.OrderBy(k => k.Name))
                {
                   Console.WriteLine($"\n【{cmd.Group}】  {cmd.Name}");
                    if (!string.IsNullOrEmpty(cmd.Description))
                    {
                       Console.WriteLine($"    说明：{cmd.Description}");
                    }
                    if (!string.IsNullOrEmpty(cmd.Parameters))
                    {
                       Console.WriteLine($"    参数：{cmd.Parameters}");
                    }
                }
            }
           Console.WriteLine("\n使用方法：<命令> [参数...]");
           Console.WriteLine("查看帮助：<命令> -h 或 <命令> --help");
        }
        
      static void RegisterCommands()
        {
            commandInfos = new Dictionary<string, CommandInfo>();
            
            var methods = typeof(Program).GetMethods(BindingFlags.NonPublic | BindingFlags.Static)
                .Where(m => m.GetCustomAttribute<CommandAttribute>() != null);
            
            foreach (var method in methods)
            {
                var attr = method.GetCustomAttribute<CommandAttribute>();
                if (attr != null)
                {
                    commandInfos[attr.Name] = new CommandInfo
                    {
                        Name = attr.Name,
                        Description = attr.Description,
                        Parameters = attr.Parameters,
                        Group = attr.Group,  // 记录命令所属组
                        Action = (string[] args) => 
                        {
                            try
                            {
                                Profiler.Time(() => method.Invoke(null, [args]), attr.Name);
                            }
                            catch (TargetInvocationException ex)
                            {
                                Console.WriteLine($"执行命令出错：{ex.InnerException?.Message}");
                            }
                        }
                    };
                }
            }
            
            commands = commandInfos.ToDictionary(k => k.Key, v => v.Value.Action);
        }

    }
}