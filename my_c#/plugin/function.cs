using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swpublished;
using SolidWorksTools;
using System;
using System.IO;
using System.Runtime.InteropServices;
using tools;
using cad_tools;
using System.Diagnostics;
using SolidWorks.Interop.swconst;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;
using System.Reflection;
using System.Threading.Tasks;
using System.Text;

   namespace SolidWorksAddinStudy
{
   
    public partial class AddinStudy 
{
       [Command(1001, "打开终端", "打开 Windows 命令行终端", "终端")]
    private void OpenTerminal()
    {
        try
        {
            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = "cmd.exe",
                Arguments = "/k chcp 65001 >nul ^&^& echo === SolidWorks 插件终端 === ^&^& echo 当前目录：%CD%^&^& echo.",
                UseShellExecute = true,
                WorkingDirectory = System.Environment.CurrentDirectory,
    
            };
            
            Process.Start(psi);
            
            Debug.WriteLine("=== 已打开终端窗口 ===");
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"打开终端失败：{ex.Message}");
            swApp?.SendMsgToUser($"无法打开终端：{ex.Message}");
        }
    }

    [Command(1002, "工程图转 DWG", "将当前工程图转换为 DWG 格式并打开", "drw2dwg", (int)swDocumentTypes_e.swDocDRAWING)]
    private void Drw2Dwg()
    {
        try
        {
            if (swApp == null)
            {
                Debug.WriteLine("SolidWorks 未初始化");
                return;
            }

            ModelDoc2 swModel = (ModelDoc2)swApp.ActiveDoc;
            if (swModel == null)
            {
                Debug.WriteLine("没有打开的文档");
                swApp.SendMsgToUser("请先打开一个工程图文档");
                return;
            }

            // 使用 share 项目中的 drw2dwg 方法转换 DWG
            var dwgFileName = drw2dwg.run(swModel, swApp);
              open_cad_doc_by_name.run(dwgFileName);
              get_all_dim_style.run();
           
            
            Debug.WriteLine($"工程图已转换为 DWG: {dwgFileName}");
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"工程图转换失败：{ex.Message}");
            swApp?.SendMsgToUser($"工程图转换失败：{ex.Message}");
        }
    }
    [Command(1003, "工程图转 DXF", "将当前工程图转换为 DXF 格式并打开", "drw2dxf", (int)swDocumentTypes_e.swDocDRAWING)]
    private void Drw2dxf()
    {
        try
        {
            if (swApp == null)
            {
                Debug.WriteLine("SolidWorks 未初始化");
                return;
            }

            ModelDoc2 swModel = (ModelDoc2)swApp.ActiveDoc;
            if (swModel == null)
            {
                Debug.WriteLine("没有打开的文档");
                swApp.SendMsgToUser("请先打开一个工程图文档");
                return;
            }

            // 使用 share 项目中的 drw2dwg 方法转换 DWG
            var dwgFileName = drw2dxf.run(swModel, swApp);
              open_cad_doc_by_name.run(dwgFileName);
              get_all_dim_style.run();
           
            
            Debug.WriteLine($"工程图已转换为 DWG: {dwgFileName}");
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"工程图转换失败：{ex.Message}");
            swApp?.SendMsgToUser($"工程图转换失败：{ex.Message}");
        }
    }

 

       
      
      

     

}}