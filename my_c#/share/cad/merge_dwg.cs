using Autodesk.AutoCAD.Interop;
using Autodesk.AutoCAD.Interop.Common;

using System.IO;

namespace cad_tools
{
    public class merge_dwg
    {
        static public void run(string sourcePath, double yOffset = 0.0, int fileIndex = 0)
        {
            if (sourcePath.Contains(".dwl2") || sourcePath.Contains(".dwl"))
            {
                
                return;
            }
            AcadApplication? acadApp = CadConnect.GetOrCreateInstance();
            if (acadApp == null)
            {
                Console.WriteLine("错误：无法连接到 AutoCAD 应用程序。");
                return;
            }

            AcadDocument? acadDoc = acadApp.ActiveDocument;
            if (acadDoc == null)
            {
                Console.WriteLine("错误：没有活动的 AutoCAD 文档。");
                return;
            }

            try
            {
                double offsetX = 500;
                double baseOffsetX = 500.0; // X 方向基础偏移量
                // 直接使用文件序号乘以偏移量 + 基础偏移
                double insertX = fileIndex * offsetX + baseOffsetX;

                string xrefPath = sourcePath;
                string baseName = Path.GetFileNameWithoutExtension(xrefPath);
                string xrefName = $"{baseName}_{Guid.NewGuid():N}";

                object insertionPoint = new double[] { insertX, yOffset, 0.0 };
                acadDoc.ModelSpace.AttachExternalReference(
                    xrefPath,
                    xrefName,
                    insertionPoint,
                    1.0, 1.0, 1.0,
                    0.0,
                    false
                );
            
                Console.WriteLine($"成功附加外部参照：{xrefName}，插入位置 X = {insertX:F2}, Y = {yOffset:F2}, 文件序号={fileIndex}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"操作失败：{ex.Message},{sourcePath}");
                if (ex.InnerException != null)
                    Console.WriteLine($"内部异常：{ex.InnerException.Message}");
            }
        }
    }
}