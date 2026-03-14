using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;

namespace tools
{
    public class add_name2info
    {
        static public void run(ModelDoc2 swModel)
        {
            try
            {
                string pathname = Path.GetFileNameWithoutExtension(swModel.GetPathName());
                 swModel.AddCustomInfo2("名称", (int)swCustomInfoType_e.swCustomInfoText, pathname);
             
                swModel.EditRebuild3();
       

            }
            catch (Exception ex)
            {
                Console.WriteLine($"发生错误: {ex.Message}");
                Console.WriteLine("提示：请确保 SolidWorks 正在运行。");
            }
        }
    }
}